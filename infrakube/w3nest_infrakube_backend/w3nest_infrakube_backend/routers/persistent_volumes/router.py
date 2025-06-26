"""
Module gathering the definition of endpoints.
"""

import asyncio

from fastapi import APIRouter, Depends, Request
from kubernetes_asyncio import client as k8s_client

from w3nest_infrakube_backend.environment import (
    Configuration,
    Environment,
    format_entry_message,
    log_resp,
)

from .schemas import PersistentVolumeList

# Disable because falsy detection of code-duplication
# pylint: disable=duplicate-code
router = APIRouter()

TOPIC_ICON = "🗄️"


@router.get(
    "/contexts/{k8s_ctx}/persistent-volumes", response_model=PersistentVolumeList
)
async def get_volumes(
    request: Request,
    k8s_ctx: str,
    config: Configuration = Depends(Environment.get_config),
) -> PersistentVolumeList:

    async with config.context(request).start(
        action=format_entry_message(TOPIC_ICON, "List Persistent Volumes"),
        with_attributes={"k8s_ctx": k8s_ctx},
    ) as ctx:
        k8s_api = await Environment.get_k8s_api(k8s_ctx)
        v1 = k8s_client.CoreV1Api(k8s_api)
        pv_list, pvc_list = await asyncio.gather(
            v1.list_persistent_volume(),
            v1.list_persistent_volume_claim_for_all_namespaces(),
        )
        pv_names = [pv.metadata.name for pv in pv_list.items]
        matching_pvcs = [
            pvc for pvc in pvc_list.items if pvc.spec.volume_name in pv_names
        ]
        namespaces = {pvc.metadata.namespace for pvc in matching_pvcs}
        all_pods = await asyncio.gather(
            *[v1.list_namespaced_pod(namespace) for namespace in namespaces]
        )
        pods = [p for pods_namespace in all_pods for p in pods_namespace.items]
        return await log_resp(
            PersistentVolumeList.from_k8s(
                k8s_ctx=k8s_ctx, pv_list=pv_list, pvc_list=pvc_list, pods=pods
            ),
            ctx,
        )
