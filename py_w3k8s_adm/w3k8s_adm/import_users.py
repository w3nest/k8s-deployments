import asyncio
import json

from w3nest_client.oidc import OidcConfig, PrivateClient, KeycloakUsersManagement
from w3nest_client.common.cache import LocalCacheClient

from w3k8s_adm.k8s_utils import (
    get_config_map,
    get_k8s_config,
    get_secret,
)

from w3nest_client import Context

# Provide here the list of users retrieved from keycloak backup
users = []


async def import_users(k8s_ctx: str):
    ctx = Context()
    k8s_config = await get_k8s_config(k8s_ctx)
    cluster = await get_config_map(
        k8s_config=k8s_config, namespace="apps", config_map="cluster-config"
    )

    print(f"✅ Successfully retrieved K8s configuration for context '{k8s_ctx}'")
    domain = cluster.data["clusterDomain"]

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
    await users_management.partial_users_import(users=users, context=ctx)


asyncio.run(import_users(k8s_ctx="minikube-ovh"))
