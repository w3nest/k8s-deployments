import asyncio

from fastapi import APIRouter
from kubernetes_asyncio import client as k8s_client
from kubernetes_asyncio.client.api_client import ApiClient

from w3nest_infrakube_backend.environment import Environment

from .schemas import NodeList

# Disable because falsy detection of code-duplication
# pylint: disable=duplicate-code
router = APIRouter()


@router.get("/contexts/{k8s_ctx}/nodes", response_model=NodeList)
async def get_nodes(k8s_ctx: str) -> NodeList:
    async with ApiClient(
        configuration=await Environment.get_k8s_config(k8s_ctx=k8s_ctx)
    ) as k8s_api:
        v1 = k8s_client.CoreV1Api(k8s_api)
        nodes, pods = await asyncio.gather(
            v1.list_node(), v1.list_pod_for_all_namespaces()
        )

        return NodeList.from_k8s(k8s_ctx=k8s_ctx, nodes=nodes, pods=pods)
