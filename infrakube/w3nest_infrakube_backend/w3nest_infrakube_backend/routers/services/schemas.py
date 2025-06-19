"""
Module gathering the schemas of bodies and responses of the end points.
"""

from kubernetes_asyncio.client import V1Pod, V1Service, V1ServiceList
from pydantic import BaseModel

from w3nest_infrakube_backend.routers.pods.schemas import PodRef
from w3nest_infrakube_backend.schemas import ResourceBase


class PortForwardBody(BaseModel):
    port: int


class PortForwardResponse(BaseModel):
    port: int
    url: str
    pid: int


class Service(ResourceBase):
    pods: list[PodRef]
    type: str

    @staticmethod
    def from_k8s(k8s_ctx: str, service: V1Service, pods: list[V1Pod]):
        return Service(
            **ResourceBase.from_k8s_base(
                k8s_ctx=k8s_ctx, resource=service, kind="Service"
            ).dict(),
            pods=[PodRef.from_k8s(k8s_ctx=k8s_ctx, pod=p) for p in pods],
            type=service.spec.type
        )


class ServiceRef(BaseModel):
    name: str
    namespace: str
    context: str

    @staticmethod
    def from_k8s(k8s_ctx: str, service: V1Service):
        return ServiceRef(
            context=k8s_ctx,
            name=service.metadata.name,
            namespace=service.metadata.namespace,
        )


class ServiceList(BaseModel):
    items: list[ServiceRef]

    @staticmethod
    def from_k8s(k8s_ctx: str, services: V1ServiceList):
        return ServiceList(
            items=[
                ServiceRef.from_k8s(k8s_ctx=k8s_ctx, service=s) for s in services.items
            ],
        )
