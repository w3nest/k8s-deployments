from fastapi import APIRouter, Depends, Request
from kubernetes_asyncio import client as k8s_client
from kubernetes_asyncio.client.api_client import ApiClient

from w3nest_infrakube_backend.environment import (
    Configuration,
    Environment,
    format_entry_message,
)

from .schemas import Secret, SecretList

# Disable because falsy detection of code-duplication
# pylint: disable=duplicate-code
router = APIRouter()

TOPIC_ICON = "🔑"


@router.get(
    "/contexts/{k8s_ctx}/namespaces/{namespace_name}/secrets",
    response_model=SecretList,
)
async def get_secrets(
    request: Request,
    k8s_ctx: str,
    namespace_name: str,
    config: Configuration = Depends(Environment.get_config),
) -> SecretList:

    async with config.context(request).start(
        action=format_entry_message(TOPIC_ICON, "List Secrets"),
        with_attributes={"k8s_ctx": k8s_ctx, "namespace_name": namespace_name},
    ):
        k8s_api = await Environment.get_k8s_api(k8s_ctx)
        v1 = k8s_client.CoreV1Api(k8s_api)
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
    request: Request,
    k8s_ctx: str,
    namespace_name: str,
    secret_name: str,
    config: Configuration = Depends(Environment.get_config),
) -> Secret:

    async with config.context(request).start(
        action=format_entry_message(TOPIC_ICON, "Get Secret"),
        with_attributes={
            "k8s_ctx": k8s_ctx,
            "namespace_name": namespace_name,
            "secret_name": secret_name,
        },
    ):
        return await get_secret(
            k8s_ctx=k8s_ctx, namespace_name=namespace_name, secret_name=secret_name
        )
