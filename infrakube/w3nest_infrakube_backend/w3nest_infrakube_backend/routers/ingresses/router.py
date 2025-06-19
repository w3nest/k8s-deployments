from fastapi import APIRouter
from kubernetes_asyncio import client as k8s_client
from kubernetes_asyncio.client.api_client import ApiClient

from w3nest_infrakube_backend.environment import Environment

from .schemas import Ingress, IngressList

router = APIRouter()


@router.get(
    "/contexts/{k8s_ctx}/namespaces/{namespace_name}/ingresses",
    response_model=IngressList,
)
async def get_ingresses(
    k8s_ctx: str,
    namespace_name: str,
) -> IngressList:

    async with ApiClient(
        configuration=await Environment.get_k8s_config(k8s_ctx=k8s_ctx)
    ) as k8s_api:
        networking_v1 = k8s_client.NetworkingV1Api(k8s_api)
        ingresses = await networking_v1.list_namespaced_ingress(
            namespace=namespace_name
        )

        return IngressList.from_k8s(k8s_ctx=k8s_ctx, ingresses=ingresses)


@router.get(
    "/contexts/{k8s_ctx}/namespaces/{namespace_name}/ingresses/{ingress_name}",
    response_model=Ingress,
)
async def get_ingress(
    k8s_ctx: str,
    namespace_name: str,
    ingress_name: str,
) -> Ingress:

    async with ApiClient(
        configuration=await Environment.get_k8s_config(k8s_ctx=k8s_ctx)
    ) as k8s_api:
        networking_v1 = k8s_client.NetworkingV1Api(k8s_api)
        ingress = await networking_v1.read_namespaced_ingress(
            name=ingress_name, namespace=namespace_name
        )

        return Ingress.from_k8s(k8s_ctx=k8s_ctx, ingress=ingress)
