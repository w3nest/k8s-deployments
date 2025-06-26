import asyncio

from fastapi import APIRouter, Depends, Request
from kubernetes_asyncio import client as k8s_client

from w3nest_infrakube_backend.environment import (
    Configuration,
    Environment,
    format_entry_message,
    log_resp,
)

from .schemas import NodeList

# Disable because falsy detection of code-duplication
# pylint: disable=duplicate-code
router = APIRouter()

TOPIC_ICON = "🔘"


@router.get("/contexts/{k8s_ctx}/nodes", response_model=NodeList)
async def get_nodes(
    request: Request,
    k8s_ctx: str,
    config: Configuration = Depends(Environment.get_config),
) -> NodeList:
    async with config.context(request).start(
        action=format_entry_message(TOPIC_ICON, "List Nodes"),
        with_attributes={"k8s_ctx": k8s_ctx},
    ) as ctx:
        k8s_api = await Environment.get_k8s_api(k8s_ctx)
        v1 = k8s_client.CoreV1Api(k8s_api)
        nodes, pods = await asyncio.gather(
            v1.list_node(), v1.list_pod_for_all_namespaces()
        )
        return await log_resp(
            NodeList.from_k8s(k8s_ctx=k8s_ctx, nodes=nodes, pods=pods), ctx
        )
