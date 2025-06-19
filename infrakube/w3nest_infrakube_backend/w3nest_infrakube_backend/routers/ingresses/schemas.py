from kubernetes_asyncio.client import (
    V1HTTPIngressPath,
    V1Ingress,
    V1IngressList,
    V1IngressServiceBackend,
    V1IngressTLS,
)
from pydantic import BaseModel

from w3nest_infrakube_backend.schemas import ResourceBase


class HttpIngressPath(BaseModel):
    backend: str
    path: str
    port: int | None

    @staticmethod
    def from_k8s(path: V1HTTPIngressPath):
        return HttpIngressPath(
            backend=path.backend.service.name,
            path=path.path,
            port=path.backend.service.port.number,
        )


class IngressServiceRef(BaseModel):
    name: str
    port: int | None

    @staticmethod
    def from_k8s(backend: V1IngressServiceBackend):
        return IngressServiceRef(
            name=backend.service.name, port=backend.service.port.number
        )


class HTTPIngressPath(BaseModel):

    service: IngressServiceRef
    path: str

    @staticmethod
    def from_k8s(http_ingress: V1HTTPIngressPath):
        return HTTPIngressPath(
            service=IngressServiceRef.from_k8s(backend=http_ingress.backend),
            path=http_ingress.path,
        )


class IngressRule(HTTPIngressPath):
    host: str
    urlBase: str


class IngressTLS(BaseModel):
    hosts: list[str]
    secretName: str

    @staticmethod
    def from_k8s(tls: V1IngressTLS):
        return IngressTLS(hosts=tls.hosts, secretName=tls.secret_name)


class Ingress(ResourceBase):
    rules: list[IngressRule]
    tls: list[IngressTLS]

    @staticmethod
    def from_k8s(k8s_ctx: str, ingress: V1Ingress):
        tls_hosts = (
            [host for tls in ingress.spec.tls for host in tls.hosts]
            if ingress.spec.tls
            else []
        )

        def with_scheme(host: str):
            if host in tls_hosts:
                return f"https://{host}"
            return f"http://{host}"

        rules_flattened = [
            IngressRule(
                host=r.host,
                urlBase=f"{with_scheme(r.host)}{p.path.split('(')[0]}",
                **HTTPIngressPath.from_k8s(http_ingress=p).dict(),
            )
            for r in ingress.spec.rules
            for p in r.http.paths
        ]
        tls = (
            [IngressTLS.from_k8s(tls) for tls in ingress.spec.tls]
            if ingress.spec.tls
            else []
        )
        return Ingress(
            **ResourceBase.from_k8s_base(
                k8s_ctx=k8s_ctx, resource=ingress, kind="Ingress"
            ).dict(),
            rules=rules_flattened,
            tls=tls,
        )


class IngressRef(BaseModel):
    name: str
    namespace: str
    context: str

    @staticmethod
    def from_k8s(k8s_ctx: str, ingress: V1Ingress):
        return IngressRef(
            context=k8s_ctx,
            name=ingress.metadata.name,
            namespace=ingress.metadata.namespace,
        )


class IngressList(BaseModel):
    context: str
    items: list[IngressRef]

    @staticmethod
    def from_k8s(k8s_ctx: str, ingresses: V1IngressList):
        return IngressList(
            context=k8s_ctx,
            items=[
                IngressRef.from_k8s(k8s_ctx=k8s_ctx, ingress=ingress)
                for ingress in ingresses.items
            ],
        )
