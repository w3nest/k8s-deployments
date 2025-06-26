import asyncio

from fastapi import APIRouter, Depends, Request
from kubernetes_asyncio import client as k8s_client

from w3nest_infrakube_backend.environment import (
    Configuration,
    Environment,
    format_entry_message,
    log_resp,
)

from .schemas import Namespace, NamespaceList

# Disable because falsy detection of code-duplication
# pylint: disable=duplicate-code
router = APIRouter()

TOPIC_ICON = "📁"


@router.get("/contexts/{k8s_ctx}/namespaces", response_model=NamespaceList)
async def get_namespaces(
    request: Request,
    k8s_ctx: str,
    config: Configuration = Depends(Environment.get_config),
) -> NamespaceList:

    async with config.context(request).start(
        action=format_entry_message(TOPIC_ICON, "List Namespaces"),
        with_attributes={
            "k8s_ctx": k8s_ctx,
        },
    ) as ctx:
        k8s_api = await Environment.get_k8s_api(k8s_ctx=k8s_ctx)
        v1 = k8s_client.CoreV1Api(k8s_api)
        namespaces = await v1.list_namespace()
        return await log_resp(
            NamespaceList.from_k8s(k8s_ctx=k8s_ctx, namespaces=namespaces), ctx
        )


@router.get("/contexts/{k8s_ctx}/namespaces/{namespace_name}", response_model=Namespace)
async def get_namespace(
    request: Request,
    k8s_ctx: str,
    namespace_name: str,
    config: Configuration = Depends(Environment.get_config),
) -> Namespace:

    async with config.context(request).start(
        action=format_entry_message(TOPIC_ICON, "Get Namespace"),
        with_attributes={
            "k8s_ctx": k8s_ctx,
            "namespace_name": namespace_name,
        },
    ) as ctx:
        k8s_api = await Environment.get_k8s_api(k8s_ctx=k8s_ctx)
        v1 = k8s_client.CoreV1Api(k8s_api)
        networking_v1 = k8s_client.NetworkingV1Api(k8s_api)

        namespace, pods, services, secrets, service_accounts, ingresses = (
            await asyncio.gather(
                v1.read_namespace(name=namespace_name),
                v1.list_namespaced_pod(namespace=namespace_name),
                v1.list_namespaced_service(namespace=namespace_name),
                v1.list_namespaced_secret(namespace=namespace_name),
                v1.list_namespaced_service_account(namespace=namespace_name),
                networking_v1.list_namespaced_ingress(namespace=namespace_name),
            )
        )

        return await log_resp(
            Namespace.from_k8s(
                k8s_ctx=k8s_ctx,
                resource=namespace,
                pods=pods,
                services=services,
                secrets=secrets,
                service_accounts=service_accounts,
                ingresses=ingresses,
            ),
            ctx,
        )
