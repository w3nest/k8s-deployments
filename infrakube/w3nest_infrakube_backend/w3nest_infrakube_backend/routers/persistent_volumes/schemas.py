from typing import Literal

from kubernetes_asyncio.client import (
    V1PersistentVolume,
    V1PersistentVolumeClaimList,
    V1PersistentVolumeList,
    V1Pod,
)
from pydantic import BaseModel

from w3nest_infrakube_backend.routers.pods import PodRef
from w3nest_infrakube_backend.schemas import ResourceBase


class PersistentVolume(ResourceBase):
    status: Literal["Bound", "Available"]
    capacity: str
    accessModes: list[str]
    storageClass: str
    reclaimPolicy: str
    volumeMode: str | None
    pods: list[PodRef]

    @staticmethod
    def from_k8s(
        k8s_ctx: str,
        pv: V1PersistentVolume,
        pvc_list: V1PersistentVolumeClaimList,
        pods: list[V1Pod],
    ):

        def get_claims(pod: V1Pod):
            return [
                vol.persistent_volume_claim.claim_name
                for vol in pod.spec.volumes
                if vol.persistent_volume_claim
            ]

        matching_pvc = next(
            pvc for pvc in pvc_list.items if pvc.spec.volume_name == pv.metadata.name
        )

        pods_on_pvc = [
            pod for pod in pods if matching_pvc.metadata.name in get_claims(pod)
        ]

        return PersistentVolume(
            **ResourceBase.from_k8s_base(
                k8s_ctx=k8s_ctx, resource=pv, kind="PersistentVolume"
            ).dict(),
            status=pv.status.phase,
            capacity=pv.spec.capacity.get("storage", "N/A"),
            accessModes=pv.spec.access_modes,
            storageClass=pv.spec.storage_class_name,
            reclaimPolicy=pv.spec.persistent_volume_reclaim_policy,
            volumeMode=pv.spec.volume_mode,
            pods=[PodRef.from_k8s(k8s_ctx=k8s_ctx, pod=pod) for pod in pods_on_pvc]
        )


class PersistentVolumeList(BaseModel):
    context: str
    items: list[PersistentVolume]

    @staticmethod
    def from_k8s(
        k8s_ctx: str,
        pv_list: V1PersistentVolumeList,
        pvc_list: V1PersistentVolumeClaimList,
        pods: list[V1Pod],
    ):
        return PersistentVolumeList(
            context=k8s_ctx,
            items=[
                PersistentVolume.from_k8s(
                    k8s_ctx=k8s_ctx, pv=pv, pvc_list=pvc_list, pods=pods
                )
                for pv in pv_list.items
            ],
        )
