import asyncio
import json

from fastapi import APIRouter
from kubernetes_asyncio import client as k8s_client
from kubernetes_asyncio.client.api_client import ApiClient

from w3nest_infrakube_backend.environment import Environment

from .schemas import GetLogsResponse, LogEntry, Pod, PodList

# Disable because falsy detection of code-duplication
# pylint: disable=duplicate-code
router = APIRouter()


@router.get(
    "/contexts/{k8s_ctx}/namespaces/{namespace_name}/pods",
    response_model=PodList,
)
async def get_pods(
    k8s_ctx: str,
    namespace_name: str,
) -> PodList:
    async with ApiClient(
        configuration=await Environment.get_k8s_config(k8s_ctx=k8s_ctx)
    ) as api:
        v1 = k8s_client.CoreV1Api(api)
        pods = await v1.list_namespaced_pod(namespace=namespace_name)
        return PodList.from_k8s(k8s_ctx=k8s_ctx, pods=pods)


@router.get(
    "/contexts/{k8s_ctx}/namespaces/{namespace}/pods/{pod_name}",
    response_model=Pod,
)
async def get_pod(
    k8s_ctx: str,
    namespace: str,
    pod_name: str,
) -> Pod:

    async with ApiClient(
        configuration=await Environment.get_k8s_config(k8s_ctx=k8s_ctx)
    ) as api:

        v1 = k8s_client.CoreV1Api(api)
        metrics_v1 = k8s_client.CustomObjectsApi(api)

        pod, metrics = await asyncio.gather(
            v1.read_namespaced_pod(name=pod_name, namespace=namespace),
            metrics_v1.list_namespaced_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                namespace=namespace,
                plural="pods",
            ),
        )
        return Pod.from_k8s(k8s_ctx=k8s_ctx, pod=pod, metrics=metrics)


@router.get(
    "/contexts/{k8s_ctx}/namespaces/{namespace}/pods/{pod}/logs",
    response_model=GetLogsResponse,
)
async def get_logs(
    k8s_ctx: str,
    namespace: str,
    pod: str,
) -> GetLogsResponse:

    def process_log(l: str):
        ts, content = l[0:30], l[31:]
        message = content
        data = {}
        if content[0] == "{":
            data = json.loads(content)
            message = data["message"]
        return LogEntry(timestamp=ts, message=message, data=data)

    async with ApiClient(
        configuration=await Environment.get_k8s_config(k8s_ctx=k8s_ctx)
    ) as api:
        v1 = k8s_client.CoreV1Api(api)
        logs = await v1.read_namespaced_pod_log(
            name=pod, namespace=namespace, since_seconds=5 * 60, timestamps=True
        )
        processed = [process_log(l) for l in logs.split("\n") if l]
        return GetLogsResponse(logs=[p for p in processed if p])
