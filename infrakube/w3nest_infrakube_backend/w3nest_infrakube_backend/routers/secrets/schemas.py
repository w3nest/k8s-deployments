"""
Module gathering the schemas of bodies and responses of the end points.
"""

import base64

from kubernetes_asyncio.client import V1Secret, V1SecretList
from pydantic import BaseModel

from w3nest_infrakube_backend.schemas import ResourceBase


class SecretRef(BaseModel):
    name: str
    context: str
    namespace: str

    @staticmethod
    def from_k8s(k8s_ctx: str, secret: V1Secret):

        return SecretRef(
            name=secret.metadata.name,
            namespace=secret.metadata.namespace,
            context=k8s_ctx,
        )


class SecretList(BaseModel):

    items: list[SecretRef]

    @staticmethod
    def from_k8s(k8s_ctx: str, secrets: V1SecretList):

        return SecretList(
            items=[SecretRef.from_k8s(k8s_ctx=k8s_ctx, secret=s) for s in secrets.items]
        )


class Secret(ResourceBase):

    data: dict[str, str]

    @staticmethod
    def from_k8s(k8s_ctx: str, secret: V1Secret):

        secret_data = {
            key: base64.b64decode(value).decode("utf-8")
            for key, value in secret.data.items()
        }

        return Secret(
            **ResourceBase.from_k8s_base(
                k8s_ctx=k8s_ctx, resource=secret, kind="Secret"
            ).dict(),
            data=secret_data
        )
