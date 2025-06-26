from fastapi import APIRouter, Depends, Request
from kubernetes_asyncio import client as k8s_client
from kubernetes_asyncio.client.api_client import ApiClient

from w3nest_infrakube_backend.environment import (
    Configuration,
    Environment,
    format_entry_message,
    log_resp,
)

from .schemas import ConfigMap, ConfigMapList

router = APIRouter()

TOPIC_ICON = "🗃️"


@router.get(
    "/contexts/{k8s_ctx}/namespaces/{namespace_name}/config-maps",
    response_model=ConfigMapList,
)
async def get_config_maps(
    request: Request,
    k8s_ctx: str,
    namespace_name: str,
    config: Configuration = Depends(Environment.get_config),
) -> ConfigMapList:

    async with config.context(request).start(
        action=format_entry_message(TOPIC_ICON, "List Config Maps"),
        with_attributes={"k8s_ctx": k8s_ctx, "namespace": namespace_name},
    ) as ctx:
        k8s_api = await Environment.get_k8s_api(k8s_ctx=k8s_ctx)
        v1 = k8s_client.CoreV1Api(k8s_api)
        config_maps = await v1.list_namespaced_config_map(namespace=namespace_name)
        return await log_resp(
            ConfigMapList.from_k8s(k8s_ctx=k8s_ctx, config_maps=config_maps), ctx
        )


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
    request: Request,
    k8s_ctx: str,
    namespace_name: str,
    config_name: str,
    config: Configuration = Depends(Environment.get_config),
) -> ConfigMap:

    async with config.context(request).start(
        action=format_entry_message(TOPIC_ICON, "Get Config Map"),
        with_attributes={
            "k8s_ctx": k8s_ctx,
            "namespace": namespace_name,
            "config_name": config_name,
        },
    ) as ctx:

        r = await get_config_map(
            k8s_ctx=k8s_ctx, namespace_name=namespace_name, config_name=config_name
        )
        return await log_resp(r, ctx)
