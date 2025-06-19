import asyncio

from w3nest_client.oidc import OidcConfig, PrivateClient, KeycloakUsersManagement
from w3nest_client.common.cache import LocalCacheClient
from w3nest_client import AnyDict, Context
from w3nest_infrakube_backend.routers.config_maps.router import get_config_map
from w3nest_infrakube_backend.routers.secrets.router import get_secret
from w3nest_infrakube_backend.w3nest_infrakube_backend.routers.w3nest.router import (
    users_mgr_client,
)

# Provide here the list of users retrieved from keycloak backup
users: list[AnyDict] = []


async def import_users(k8s_ctx: str):
    ctx = Context()
    users_management = await users_mgr_client(k8s_ctx=k8s_ctx)
    # users_ = await users_management.get_users_with_query(first=0, q="", context=ctx)
    await users_management.partial_users_import(users=users, context=ctx)


asyncio.run(import_users(k8s_ctx="minikube-ovh"))
