from fastapi import APIRouter
from kubernetes_asyncio import config as k8s_config
from kubernetes_asyncio.client.api_client import ApiClient

from w3nest_infrakube_backend.environment import Environment

from .schemas import Context, ContextList

router = APIRouter()


@router.get("/contexts", response_model=ContextList)
async def get_contexts() -> ContextList:
    k8s_contexts, _active_ctx = k8s_config.list_kube_config_contexts(
        config_file=str(Environment.config_path)
    )

    return ContextList(
        items=[
            Context(
                cluster=c["context"]["cluster"],
                user=c["context"]["user"],
                name=c["name"],
            )
            for c in k8s_contexts
        ]
    )


@router.get("/contexts/{k8s_ctx}", response_model=Context)
async def get_context(
    k8s_ctx: str,
) -> Context:
    async with ApiClient(
        configuration=await Environment.get_k8s_config(k8s_ctx=k8s_ctx)
    ):
        contexts, _ = k8s_config.list_kube_config_contexts(
            config_file=str(Environment.config_path)
        )
        c = next((c for c in contexts if c["name"] == k8s_ctx))

        return Context(
            cluster=c["context"]["cluster"], user=c["context"]["user"], name=c["name"]
        )
