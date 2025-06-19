from typing import Literal

from kubernetes_asyncio.client import V1Node, V1NodeList, V1PodList
from pydantic import BaseModel

from w3nest_infrakube_backend.routers.pods import PodRef
from w3nest_infrakube_backend.schemas import ResourceBase


def get_node_addresses(node: V1Node):
    internal = None
    external = None
    host = None
    for addr in node.status.addresses:
        if addr.type == "InternalIP":
            internal = addr.address
        if addr.type == "ExternalIP":
            external = addr.address
        if addr.type == "Hostname":
            host = addr.address
    return internal, external, host


def get_node_status(node: V1Node) -> Literal["Ready", "Not Ready", "Unknown"]:
    for condition in node.status.conditions:
        if condition.type == "Ready":
            return "Ready" if condition.status == "True" else "Not Ready"
    return "Unknown"


class Node(ResourceBase):
    status: Literal["Ready", "Not Ready", "Unknown"]
    cpuCapacity: str
    memoryCapacity: str
    internalIp: str
    externalIp: str | None
    hostname: str | None
    pods: list[PodRef]

    @staticmethod
    def from_k8s(k8s_ctx: str, node: V1Node, pods: V1PodList):

        internal_ip, external_ip, hostname = get_node_addresses(node)

        pods_on_node = [
            pod for pod in pods.items if pod.spec.node_name == node.metadata.name
        ]

        return Node(
            **ResourceBase.from_k8s_base(
                k8s_ctx=k8s_ctx, resource=node, kind="Node"
            ).dict(),
            status=get_node_status(node),
            cpuCapacity=node.status.capacity["cpu"],
            memoryCapacity=node.status.capacity["memory"],
            internalIp=internal_ip,
            externalIp=external_ip,
            hostname=hostname,
            pods=[PodRef.from_k8s(k8s_ctx=k8s_ctx, pod=p) for p in pods_on_node]
        )


class NodeList(BaseModel):
    k8s_ctx: str
    items: list[Node]

    @staticmethod
    def from_k8s(k8s_ctx: str, nodes: V1NodeList, pods: V1PodList):
        return NodeList(
            k8s_ctx=k8s_ctx,
            items=[
                Node.from_k8s(k8s_ctx=k8s_ctx, node=node, pods=pods)
                for node in nodes.items
            ],
        )
