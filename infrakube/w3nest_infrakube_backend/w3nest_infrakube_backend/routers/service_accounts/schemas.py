"""
Module gathering the schemas of bodies and responses of the end points.
"""

from kubernetes_asyncio.client import (
    AuthenticationV1TokenRequest,
    V1ServiceAccount,
    V1ServiceAccountList,
)
from pydantic import BaseModel

from w3nest_infrakube_backend.schemas import ResourceBase


class ServiceAccountRef(BaseModel):
    name: str
    context: str
    namespace: str

    @staticmethod
    def from_k8s(k8s_ctx: str, sa: V1ServiceAccount):

        return ServiceAccountRef(
            name=sa.metadata.name,
            namespace=sa.metadata.namespace,
            context=k8s_ctx,
        )


class ServiceAccountList(BaseModel):

    items: list[ServiceAccountRef]

    @staticmethod
    def from_k8s(k8s_ctx: str, service_accounts: V1ServiceAccountList):

        return ServiceAccountList(
            items=[
                ServiceAccountRef.from_k8s(k8s_ctx=k8s_ctx, sa=s)
                for s in service_accounts.items
            ]
        )


class ServiceAccount(ResourceBase):

    @staticmethod
    def from_k8s(k8s_ctx: str, service_account: V1ServiceAccount):

        return ServiceAccount(
            **ResourceBase.from_k8s_base(
                k8s_ctx=k8s_ctx, resource=service_account, kind="ServiceAccount"
            ).dict(),
        )


class TokenResponse(ResourceBase):
    token: str
    expiration: float
    audiences: list[str]

    @staticmethod
    def from_k8s(k8s_ctx: str, token: AuthenticationV1TokenRequest):

        return TokenResponse(
            **ResourceBase.from_k8s_base(
                k8s_ctx=k8s_ctx, resource=token, kind="AuthenticationToken"
            ).dict(),
            token=token.status.token,
            expiration=float(token.status.expiration_timestamp.timestamp()),
            audiences=token.spec.audiences,
        )
