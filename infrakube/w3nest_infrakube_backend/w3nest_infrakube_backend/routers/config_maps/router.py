from fastapi import APIRouter
from kubernetes_asyncio import client as k8s_client
from kubernetes_asyncio.client.api_client import ApiClient

from w3nest_infrakube_backend.environment import Environment

from .schemas import ConfigMap, ConfigMapList

router = APIRouter()


@router.get(
    "/contexts/{k8s_ctx}/namespaces/{namespace_name}/config-maps",
    response_model=ConfigMapList,
)
async def get_config_maps(
    k8s_ctx: str,
    namespace_name: str,
) -> ConfigMapList:

    async with ApiClient(
        configuration=await Environment.get_k8s_config(k8s_ctx=k8s_ctx)
    ) as api:

        v1 = k8s_client.CoreV1Api(api)
        config_maps = await v1.list_namespaced_config_map(namespace=namespace_name)
        return ConfigMapList.from_k8s(k8s_ctx=k8s_ctx, config_maps=config_maps)


async def get_config_map(
    k8s_ctx: str,
    namespace_name: str,
    config_name: str,
) -> ConfigMap:

    async with ApiClient(
        configuration=await Environment.get_k8s_config(k8s_ctx=k8s_ctx)
    ) as api:

        v1 = k8s_client.CoreV1Api(api)
        config_map = await v1.read_namespaced_config_map(
            name=config_name, namespace=namespace_name
        )
        return ConfigMap.from_k8s(k8s_ctx=k8s_ctx, config_map=config_map)


@router.get(
    "/contexts/{k8s_ctx}/namespaces/{namespace_name}/config-maps/{config_name}",
    response_model=ConfigMap,
)
async def get_config_map_ep(
    k8s_ctx: str,
    namespace_name: str,
    config_name: str,
) -> ConfigMap:

    return await get_config_map(
        k8s_ctx=k8s_ctx, namespace_name=namespace_name, config_name=config_name
    )
