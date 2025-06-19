"""
Module gathering the schemas of bodies and responses of the end points.
"""

from typing import Any, Literal

from pydantic import BaseModel

KIND = Literal[
    "Ingress",
    "Pod",
    "Secret",
    "Service",
    "ServiceAccount",
    "AuthenticationToken",
    "Namespace",
    "Node",
    "PersistentVolume",
    "ConfigMap",
]


class ResourceBase(BaseModel):
    name: str
    context: str
    namespace: str | None
    kind: KIND
    labels: dict[str, str]
    annotations: dict[str, str]

    @staticmethod
    def from_k8s_base(
        k8s_ctx: str,
        resource: Any,
        kind: KIND | None = None,
        namespace: str | None = None,
    ):
        return ResourceBase(
            name=resource.metadata.name,
            kind=kind or resource.kind,
            context=k8s_ctx,
            namespace=resource.metadata.namespace or namespace,
            labels=resource.metadata.labels or {},
            annotations=resource.metadata.annotations or {},
        )
