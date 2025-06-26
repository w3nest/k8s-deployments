from fastapi import APIRouter, Depends, Request
from kubernetes_asyncio import config as k8s_config

from w3nest_infrakube_backend.environment import (
    Configuration,
    Environment,
    format_entry_message,
    log_resp,
)

from .schemas import Context, ContextList

router = APIRouter()

TOPIC_ICON = "🧭"


@router.get("/contexts", response_model=ContextList)
async def get_contexts(
    request: Request,
    config: Configuration = Depends(Environment.get_config),
) -> ContextList:

    async with config.context(request).start(
        action=format_entry_message(TOPIC_ICON, "List Contexts"),
    ) as ctx:

        k8s_contexts, active_ctx = k8s_config.list_kube_config_contexts(
            config_file=str(Environment.config_path)
        )
        await ctx.info(
            "Retrieved contexts",
            data={"k8s_contexts": k8s_contexts, "active_ctx": active_ctx},
        )
        return await log_resp(
            ContextList(
                items=[
                    Context(
                        cluster=c["context"]["cluster"],
                        user=c["context"]["user"],
                        name=c["name"],
                    )
                    for c in k8s_contexts
                ]
            ),
            ctx,
        )


@router.get("/contexts/{k8s_ctx}", response_model=Context)
async def get_context(
    request: Request,
    k8s_ctx: str,
    config: Configuration = Depends(Environment.get_config),
) -> Context:

    async with config.context(request).start(
        action=format_entry_message(TOPIC_ICON, "Get Context"),
    ) as ctx:
        k8s_contexts, active_ctx = k8s_config.list_kube_config_contexts(
            config_file=str(Environment.config_path)
        )

        await ctx.info(
            "Retrieved contexts",
            data={"k8s_contexts": k8s_contexts, "active_ctx": active_ctx},
        )

        c = next((c for c in k8s_contexts if c["name"] == k8s_ctx))

        return await log_resp(
            Context(
                cluster=c["context"]["cluster"],
                user=c["context"]["user"],
                name=c["name"],
            ),
            ctx,
        )
