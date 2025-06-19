"""
Module gathering the schemas of bodies and responses of the end points.
"""

from kubernetes_asyncio.client import (
    V1IngressList,
    V1Namespace,
    V1NamespaceList,
    V1PodList,
    V1SecretList,
    V1ServiceAccountList,
    V1ServiceList,
)
from pydantic import BaseModel

from w3nest_infrakube_backend.routers.ingresses import IngressRef
from w3nest_infrakube_backend.routers.pods.schemas import PodRef
from w3nest_infrakube_backend.routers.secrets import SecretRef
from w3nest_infrakube_backend.routers.service_accounts import ServiceAccountRef
from w3nest_infrakube_backend.routers.services import ServiceRef
from w3nest_infrakube_backend.schemas import ResourceBase


class NamespaceRef(BaseModel):
    name: str


class NamespaceList(BaseModel):
    context: str
    items: list[NamespaceRef]

    @staticmethod
    def from_k8s(k8s_ctx: str, namespaces: V1NamespaceList):
        return NamespaceList(
            context=k8s_ctx,
            items=[NamespaceRef(name=item.metadata.name) for item in namespaces.items],
        )


class PodsStats(BaseModel):
    totalPods: int
    runningPods: int
    pendingPods: int
    succeededPods: int
    failedPods: int
    crashLoopPods: int
    unknownPods: int
    crashLoopPodNames: list[str]

    @staticmethod
    def from_k8s(pods: V1PodList):
        total_pods = len(pods.items)
        running_pods = pending_pods = succeeded_pods = failed_pods = crash_loop_pods = (
            unknown_pods
        ) = 0

        crash_loop_pod_names = []

        for pod in pods.items:
            status = pod.status.phase

            if status == "Running":
                running_pods += 1
            elif status == "Pending":
                pending_pods += 1
            elif status == "Succeeded":
                succeeded_pods += 1
            elif status == "Failed":
                failed_pods += 1
            elif status == "Unknown":
                unknown_pods += 1

            # Check for CrashLoopBackOff in container states
            for container_status in pod.status.container_statuses or []:
                if (
                    container_status.state.waiting
                    and container_status.state.waiting.reason == "CrashLoopBackOff"
                ):
                    crash_loop_pods += 1
                    crash_loop_pod_names.append(pod.metadata.name)
                    break  # Avoid double-counting if multiple containers are in CrashLoopBackOff

        return PodsStats(
            totalPods=total_pods,
            runningPods=running_pods,
            pendingPods=pending_pods,
            succeededPods=succeeded_pods,
            failedPods=failed_pods,
            crashLoopPods=crash_loop_pods,
            unknownPods=unknown_pods,
            crashLoopPodNames=crash_loop_pod_names,
        )


class Namespace(ResourceBase):
    podsStats: PodsStats
    pods: list[PodRef]
    services: list[ServiceRef]
    ingresses: list[IngressRef]
    secrets: list[SecretRef]
    serviceAccounts: list[ServiceAccountRef]

    @staticmethod
    def from_k8s(
        k8s_ctx: str,
        resource: V1Namespace,
        pods: V1PodList,
        services: V1ServiceList,
        ingresses: V1IngressList,
        secrets: V1SecretList,
        service_accounts: V1ServiceAccountList,
    ):

        return Namespace(
            **ResourceBase.from_k8s_base(
                k8s_ctx=k8s_ctx,
                resource=resource,
                kind="Namespace",
                namespace=resource.metadata.name,
            ).dict(),
            podsStats=PodsStats.from_k8s(pods=pods),
            pods=[PodRef.from_k8s(k8s_ctx=k8s_ctx, pod=e) for e in pods.items],
            services=[
                ServiceRef.from_k8s(k8s_ctx=k8s_ctx, service=e) for e in services.items
            ],
            secrets=[
                SecretRef.from_k8s(k8s_ctx=k8s_ctx, secret=e) for e in secrets.items
            ],
            ingresses=[
                IngressRef.from_k8s(k8s_ctx=k8s_ctx, ingress=e) for e in ingresses.items
            ],
            serviceAccounts=[
                ServiceAccountRef.from_k8s(k8s_ctx=k8s_ctx, sa=e)
                for e in service_accounts.items
            ],
        )
