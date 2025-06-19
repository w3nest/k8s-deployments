import asyncio

from fastapi import APIRouter
from kubernetes_asyncio import client as k8s_client
from kubernetes_asyncio.client.api_client import ApiClient

from w3nest_infrakube_backend.environment import Environment

from .schemas import Namespace, NamespaceList

# Disable because falsy detection of code-duplication
# pylint: disable=duplicate-code
router = APIRouter()


@router.get("/contexts/{k8s_ctx}/namespaces", response_model=NamespaceList)
async def get_namespaces(
    k8s_ctx: str,
) -> NamespaceList:
    async with ApiClient(
        configuration=await Environment.get_k8s_config(k8s_ctx=k8s_ctx)
    ) as k8s_api:
        v1 = k8s_client.CoreV1Api(k8s_api)
        namespaces = await v1.list_namespace()
        return NamespaceList.from_k8s(k8s_ctx=k8s_ctx, namespaces=namespaces)


@router.get("/contexts/{k8s_ctx}/namespaces/{namespace_name}", response_model=Namespace)
async def get_namespace(
    k8s_ctx: str,
    namespace_name: str,
) -> Namespace:
    async with ApiClient(
        configuration=await Environment.get_k8s_config(k8s_ctx=k8s_ctx)
    ) as k8s_api:
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

        return Namespace.from_k8s(
            k8s_ctx=k8s_ctx,
            resource=namespace,
            pods=pods,
            services=services,
            secrets=secrets,
            service_accounts=service_accounts,
            ingresses=ingresses,
        )
