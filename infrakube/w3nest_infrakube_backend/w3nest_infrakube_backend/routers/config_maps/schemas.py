"""
Module gathering the schemas of bodies and responses of the end points.
"""

from kubernetes_asyncio.client import V1ConfigMap, V1ConfigMapList
from pydantic import BaseModel

from w3nest_infrakube_backend.schemas import ResourceBase


class ConfigMapRef(BaseModel):
    name: str
    context: str
    namespace: str

    @staticmethod
    def from_k8s(k8s_ctx: str, config_map: V1ConfigMap):

        return ConfigMapRef(
            name=config_map.metadata.name,
            namespace=config_map.metadata.namespace,
            context=k8s_ctx,
        )


class ConfigMapList(BaseModel):

    items: list[ConfigMapRef]

    @staticmethod
    def from_k8s(k8s_ctx: str, config_maps: V1ConfigMapList):

        return ConfigMapList(
            items=[
                ConfigMapRef.from_k8s(k8s_ctx=k8s_ctx, config_map=s)
                for s in config_maps.items
            ]
        )


class ConfigMap(ResourceBase):

    data: dict[str, str]

    @staticmethod
    def from_k8s(k8s_ctx: str, config_map: V1ConfigMap):

        return ConfigMap(
            **ResourceBase.from_k8s_base(
                k8s_ctx=k8s_ctx, resource=config_map, kind="ConfigMap"
            ).dict(),
            data=config_map.data
        )
