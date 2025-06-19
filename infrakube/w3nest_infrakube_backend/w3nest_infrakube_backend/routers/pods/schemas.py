"""
Module gathering the schemas of bodies and responses of the end points.
"""

from typing import Any

from kubernetes_asyncio.client import V1Container, V1Pod, V1PodList
from pydantic import BaseModel

from w3nest_infrakube_backend.schemas import ResourceBase


class PodRef(BaseModel):
    context: str
    name: str
    namespace: str

    @staticmethod
    def from_k8s(k8s_ctx: str, pod: V1Pod):

        return PodRef(
            name=pod.metadata.name,
            namespace=pod.metadata.namespace,
            context=k8s_ctx,
        )


class PodList(BaseModel):
    items: list[PodRef]

    @staticmethod
    def from_k8s(k8s_ctx: str, pods: V1PodList):
        return PodList(
            items=[PodRef.from_k8s(k8s_ctx=k8s_ctx, pod=item) for item in pods.items]
        )


class Container(BaseModel):
    name: str
    image: str
    imagePullPolicy: str
    command: list[str] | None

    @staticmethod
    def from_k8s(container: V1Container):
        return Container(
            name=container.name,
            image=container.image,
            imagePullPolicy=container.image_pull_policy,
            command=container.command,
        )


class PodResourceInfo(BaseModel):
    podIP: str
    phase: str
    qosClass: str
    serviceAccount: str
    imagePullSecrets: list[str]

    @staticmethod
    def from_k8s(pod: V1Pod):
        return PodResourceInfo(
            podIP=pod.status.pod_ip,
            phase=pod.status.phase,
            qosClass=pod.status.qos_class,
            serviceAccount=pod.spec.service_account,
            imagePullSecrets=(
                [s.name for s in pod.spec.image_pull_secrets]
                if pod.spec.image_pull_secrets
                else []
            ),
        )


class LogEntry(BaseModel):
    data: dict[str, Any] | None
    message: str
    timestamp: str


class Pod(ResourceBase):
    cpu: int  # nano
    memory: int  # Ki
    containers: list[Container]
    initContainers: list[Container]
    creationTimestamp: int
    resourceInfo: PodResourceInfo

    @staticmethod
    def from_k8s(k8s_ctx: str, pod: V1Pod, metrics: dict[str, Any]):
        if "kind" not in metrics or metrics["kind"] != "PodMetricsList":
            raise TypeError('metrics should be of kind "PodMetricsList"')
        pod_name = pod.metadata.name
        item = next(c for c in metrics["items"] if c["metadata"]["name"] == pod_name)
        containers = item["containers"]
        cpu_usage = sum((int(c["usage"]["cpu"].rstrip("n")) for c in containers))
        memory_usage = sum((int(c["usage"]["memory"].rstrip("Ki")) for c in containers))

        return Pod(
            **ResourceBase.from_k8s_base(k8s_ctx=k8s_ctx, resource=pod).dict(),
            creationTimestamp=pod.metadata.creation_timestamp.timestamp(),
            cpu=cpu_usage,
            memory=memory_usage,
            resourceInfo=PodResourceInfo.from_k8s(pod),
            containers=[Container.from_k8s(c) for c in pod.spec.containers],
            initContainers=[
                Container.from_k8s(c) for c in pod.spec.init_containers or []
            ],
        )


class GetLogsResponse(BaseModel):
    logs: list[LogEntry]
