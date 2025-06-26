import asyncio
import json

from fastapi import APIRouter, Depends, Request
from kubernetes_asyncio import client as k8s_client

from w3nest_infrakube_backend.environment import (
    Configuration,
    Environment,
    format_entry_message,
    log_resp,
)

from .schemas import GetLogsResponse, LogEntry, Pod, PodList

# Disable because falsy detection of code-duplication
# pylint: disable=duplicate-code
router = APIRouter()

TOPIC_ICON = "🥚"


@router.get(
    "/contexts/{k8s_ctx}/namespaces/{namespace_name}/pods",
    response_model=PodList,
)
async def get_pods(
    request: Request,
    k8s_ctx: str,
    namespace_name: str,
    config: Configuration = Depends(Environment.get_config),
) -> PodList:

    async with config.context(request).start(
        action=format_entry_message(TOPIC_ICON, "List Pods"),
        with_attributes={"k8s_ctx": k8s_ctx, "namespace_name": namespace_name},
    ) as ctx:

        k8s_api = await Environment.get_k8s_api(k8s_ctx)
        v1 = k8s_client.CoreV1Api(k8s_api)
        pods = await v1.list_namespaced_pod(namespace=namespace_name)
        return await log_resp(PodList.from_k8s(k8s_ctx=k8s_ctx, pods=pods), ctx)


@router.get(
    "/contexts/{k8s_ctx}/namespaces/{namespace}/pods/{pod_name}",
    response_model=Pod,
)
async def get_pod(
    request: Request,
    k8s_ctx: str,
    namespace: str,
    pod_name: str,
    config: Configuration = Depends(Environment.get_config),
) -> Pod:

    async with config.context(request).start(
        action=format_entry_message(TOPIC_ICON, "List Pods"),
        with_attributes={
            "k8s_ctx": k8s_ctx,
            "namespace_name": namespace,
            "pod_name": pod_name,
        },
    ) as ctx:

        k8s_api = await Environment.get_k8s_api(k8s_ctx)
        v1 = k8s_client.CoreV1Api(k8s_api)
        metrics_v1 = k8s_client.CustomObjectsApi(k8s_api)

        pod, metrics = await asyncio.gather(
            v1.read_namespaced_pod(name=pod_name, namespace=namespace),
            metrics_v1.list_namespaced_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                namespace=namespace,
                plural="pods",
            ),
        )
        return await log_resp(
            Pod.from_k8s(k8s_ctx=k8s_ctx, pod=pod, metrics=metrics), ctx
        )


@router.get(
    "/contexts/{k8s_ctx}/namespaces/{namespace}/pods/{pod}/logs",
    response_model=GetLogsResponse,
)
async def get_logs(
    request: Request,
    k8s_ctx: str,
    namespace: str,
    pod: str,
    config: Configuration = Depends(Environment.get_config),
) -> GetLogsResponse:

    def process_log(l: str):
        ts, content = l[0:30], l[31:]
        message = content
        data = {}
        if content[0] == "{":
            data = json.loads(content)
            message = data["message"]
        return LogEntry(timestamp=ts, message=message, data=data)

    async with config.context(request).start(
        action=format_entry_message(TOPIC_ICON, "Get Logs"),
        with_attributes={
            "k8s_ctx": k8s_ctx,
            "namespace_name": namespace,
            "pod_name": pod,
        },
    ):
        k8s_api = await Environment.get_k8s_api(k8s_ctx)
        v1 = k8s_client.CoreV1Api(k8s_api)
        logs = await v1.read_namespaced_pod_log(
            name=pod, namespace=namespace, since_seconds=5 * 60, timestamps=True
        )
        processed = [process_log(l) for l in logs.split("\n") if l]
        return GetLogsResponse(logs=[p for p in processed if p])
