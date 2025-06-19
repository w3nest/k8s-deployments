from fastapi import APIRouter
from kubernetes_asyncio import client as k8s_client
from kubernetes_asyncio.client.api_client import ApiClient

from w3nest_infrakube_backend.environment import Environment

from .schemas import Secret, SecretList

# Disable because falsy detection of code-duplication
# pylint: disable=duplicate-code
router = APIRouter()


@router.get(
    "/contexts/{k8s_ctx}/namespaces/{namespace_name}/secrets",
    response_model=SecretList,
)
async def get_secrets(
    k8s_ctx: str,
    namespace_name: str,
) -> SecretList:

    async with ApiClient(
        configuration=await Environment.get_k8s_config(k8s_ctx=k8s_ctx)
    ) as api:

        v1 = k8s_client.CoreV1Api(api)
        secrets = await v1.list_namespaced_secret(namespace=namespace_name)
        return SecretList.from_k8s(k8s_ctx=k8s_ctx, secrets=secrets)


async def get_secret(
    k8s_ctx: str,
    namespace_name: str,
    secret_name: str,
) -> Secret:

    async with ApiClient(
        configuration=await Environment.get_k8s_config(k8s_ctx=k8s_ctx)
    ) as api:

        v1 = k8s_client.CoreV1Api(api)
        secret = await v1.read_namespaced_secret(
            name=secret_name, namespace=namespace_name
        )
        return Secret.from_k8s(k8s_ctx=k8s_ctx, secret=secret)


@router.get(
    "/contexts/{k8s_ctx}/namespaces/{namespace_name}/secrets/{secret_name}",
    response_model=Secret,
)
async def get_secret_ep(
    k8s_ctx: str,
    namespace_name: str,
    secret_name: str,
) -> Secret:

    return await get_secret(
        k8s_ctx=k8s_ctx, namespace_name=namespace_name, secret_name=secret_name
    )
