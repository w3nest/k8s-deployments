import asyncio
import json

from w3nest_client.oidc import (
    OidcConfig,
    PrivateClient,
    PrivateClient,
    KeycloakUsersManagement,
)
from w3nest_client.common.cache import LocalCacheClient

from w3k8s_adm.minio_client import start_minio_client
from w3k8s_adm.k8s_utils import (
    get_config_map,
    get_k8s_config,
    get_secret,
    port_fwd_service,
)

from w3nest_client import Context

PORT_FWD_MINIO = 9143


async def delete_temp_users(k8s_ctx: str):
    ctx = Context()
    k8s_config = await get_k8s_config(k8s_ctx)
    cluster = await get_config_map(
        k8s_config=k8s_config, namespace="apps", config_map="cluster-config"
    )

    print(f"✅ Successfully retrieved K8s configuration for context '{k8s_ctx}'")
    domain = cluster.data["clusterDomain"]

    print(f"📡 Connected to '{domain}'")
    await port_fwd_service(
        k8s_config=k8s_config, namespace="infra", service="minio", port=PORT_FWD_MINIO
    )
    minio = await start_minio_client(k8s_ctx=k8s_ctx)

    obj = minio.get_object(object_name="assets/entities/data.json", bucket_name="docdb")
    assets = json.loads(obj.data)["documents"]
    print(f"📡 Successfully  '{k8s_ctx}'")

    secret: dict[str, str] = await get_secret(
        k8s_config=k8s_config,
        namespace_name="apps",
        secret_name="keycloak-admin-secret",
    )
    kc_admin_secret: str = secret["keycloak_admin_client_secret"]

    print("🔑 Got keycloak admin secret")

    oidc_config = OidcConfig(f"https://{domain}/auth/realms/youwol")

    kc_admin_client = oidc_config.for_client(
        PrivateClient(
            client_id="admin-cli",
            client_secret=kc_admin_secret,
        )
    )
    auth_cache = LocalCacheClient(prefix="kc_cache")
    users_management = KeycloakUsersManagement(
        realm_url=f"https://{domain}/auth/admin/realms/youwol",
        cache=auth_cache,
        oidc_client=kc_admin_client,
    )
    temp_users = await users_management.get_temporary_users(first=0, context=ctx)

    print(f"👥 Retrieved {len(temp_users)} guest users")
    for user in temp_users:
        print(f"🗑️ Proceeding deletion of user {user.id}...")

        owned_assets = [
            asset for asset in assets if asset["group_id"] == f"private_{user.id}"
        ]
        print(f"🔎 Found {len(owned_assets)} owned assets")
        await users_management.delete_user(user_id=user.id, context=ctx)


asyncio.run(delete_temp_users(k8s_ctx="minikube-ovh"))
