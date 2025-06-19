import json
import sys

from fastapi import APIRouter, Request
from minio import Minio
from urllib3.exceptions import MaxRetryError
from w3nest_client.common.cache import LocalCacheClient
from w3nest_client.oidc import (
    KeycloakUsersManagement,
    OidcConfig,
    PrivateClient,
)

from w3nest_infrakube_backend.environment import Environment
from w3nest_infrakube_backend.routers.config_maps.router import (
    get_config_map,
)
from w3nest_infrakube_backend.routers.secrets.router import (
    get_secret,
)
from w3nest_infrakube_backend.routers.services.router import (
    port_fwd,
)
from w3nest_infrakube_backend.routers.w3nest.models import (
    GuestUser,
)

LOKI_URL = "http://localhost:3100/loki/api/v1/query_range"

router = APIRouter()


async def minio_client(k8s_ctx: str) -> Minio:

    print(f"✅ Successfully retrieved K8s configuration for context '{k8s_ctx}'")

    port_fwd_resp = await port_fwd(
        k8s_ctx=k8s_ctx, namespace_name="infra", service_name="minio"
    )
    print("🔑 Use secret 'minio-admin-secret.admin-secret-key' for minio connection")
    secret = await get_secret(
        k8s_ctx=k8s_ctx, namespace_name="infra", secret_name="minio-admin-secret"
    )

    minio = Minio(
        endpoint=f"localhost:{port_fwd_resp.port}",
        access_key="admin",
        secret_key=secret.data["admin-secret-key"],
        secure=False,
    )
    try:
        buckets = minio.list_buckets()

        print(
            "🟢 Connected to minio, available buckets:",
            [bucket.name for bucket in buckets],
        )
    except MaxRetryError as e:
        print("🚫 Connection to minio failed:", str(e))
        sys.exit(1)

    return minio


async def users_mgr_client(k8s_ctx: str) -> KeycloakUsersManagement:

    env = await get_config_map(
        k8s_ctx=k8s_ctx, namespace_name="apps", config_name="env-config"
    )

    print(f"✅ Successfully retrieved K8s configuration for context '{k8s_ctx}'")
    keycloak_admin_uri = env.data["keycloak_admin_base_url"]
    oidc_uri = env.data["openid_base_url"]
    secret = await get_secret(
        k8s_ctx=k8s_ctx,
        namespace_name="apps",
        secret_name="keycloak-admin-secret",
    )
    kc_admin_secret: str = secret.data["keycloak_admin_client_secret"]

    print("🔑 Got keycloak admin secret")

    oidc_config = OidcConfig(oidc_uri)

    kc_admin_client = oidc_config.for_client(
        PrivateClient(
            client_id="admin-cli",
            client_secret=kc_admin_secret,
        )
    )
    auth_cache = LocalCacheClient(prefix="kc_cache")
    users_management = KeycloakUsersManagement(
        realm_url=keycloak_admin_uri,
        cache=auth_cache,
        oidc_client=kc_admin_client,
    )
    return users_management


@router.get("/contexts/{k8s_ctx}/w3nest/keycloak/guests")
async def get_guests_ep(
    request: Request,
    k8s_ctx: str,
) -> list[GuestUser]:
    async with Environment.get_config().context(request=request).start(
        action="get_guests_ep"
    ) as ctx:
        users_client = await users_mgr_client(k8s_ctx=k8s_ctx)
        resp = await users_client.get_temporary_users(first=0, context=ctx)

        return [
            GuestUser(
                id=user.id,
                username=user.username,
                createdTimestamp=user.createdTimestamp,
            )
            for user in resp
        ]


@router.delete("/contexts/{k8s_ctx}/w3nest/keycloak/guests")
async def delete_guests_ep(
    request: Request,
    k8s_ctx: str,
):
    async with Environment.get_config().context(request=request).start(
        action="delete_guests_ep"
    ) as ctx:
        users_client = await users_mgr_client(k8s_ctx=k8s_ctx)
        guests = await users_client.get_temporary_users(first=0, context=ctx)
        minio = await minio_client(k8s_ctx=k8s_ctx)
        obj = minio.get_object(
            object_name="assets/entities/data.json", bucket_name="docdb"
        )
        assets = json.loads(obj.data)["documents"]
        for user in guests:
            print(f"🗑️ Proceeding deletion of user {user.id}...")

            owned_assets = [
                asset for asset in assets if asset["group_id"] == f"private_{user.id}"
            ]
            print(f"🔎 Found {len(owned_assets)} owned assets")
            await users_client.delete_user(user_id=user.id, context=ctx)
