from fastapi import APIRouter, Depends, Request
from kubernetes_asyncio import client as k8s_client

from w3nest_infrakube_backend.environment import (
    Configuration,
    Environment,
    format_entry_message,
    log_resp,
)

from .schemas import Ingress, IngressList

router = APIRouter()

TOPIC_ICON = "🛣️"


@router.get(
    "/contexts/{k8s_ctx}/namespaces/{namespace_name}/ingresses",
    response_model=IngressList,
)
async def get_ingresses(
    request: Request,
    k8s_ctx: str,
    namespace_name: str,
    config: Configuration = Depends(Environment.get_config),
) -> IngressList:

    async with config.context(request).start(
        action=format_entry_message(TOPIC_ICON, "List Ingresses"),
        with_attributes={"k8s_ctx": k8s_ctx, "namespace": namespace_name},
    ) as ctx:
        k8s_api = await Environment.get_k8s_api(k8s_ctx=k8s_ctx)
        networking_v1 = k8s_client.NetworkingV1Api(k8s_api)
        ingresses = await networking_v1.list_namespaced_ingress(
            namespace=namespace_name
        )
        return await log_resp(
            IngressList.from_k8s(k8s_ctx=k8s_ctx, ingresses=ingresses), ctx
        )


@router.get(
    "/contexts/{k8s_ctx}/namespaces/{namespace_name}/ingresses/{ingress_name}",
    response_model=Ingress,
)
async def get_ingress(
    request: Request,
    k8s_ctx: str,
    namespace_name: str,
    ingress_name: str,
    config: Configuration = Depends(Environment.get_config),
) -> Ingress:

    async with config.context(request).start(
        action=format_entry_message(TOPIC_ICON, "Get Ingress"),
        with_attributes={
            "k8s_ctx": k8s_ctx,
            "namespace": namespace_name,
            "ingress": ingress_name,
        },
    ) as ctx:
        k8s_api = await Environment.get_k8s_api(k8s_ctx=k8s_ctx)
        networking_v1 = k8s_client.NetworkingV1Api(k8s_api)
        ingress = await networking_v1.read_namespaced_ingress(
            name=ingress_name, namespace=namespace_name
        )
        return await log_resp(Ingress.from_k8s(k8s_ctx=k8s_ctx, ingress=ingress), ctx)
