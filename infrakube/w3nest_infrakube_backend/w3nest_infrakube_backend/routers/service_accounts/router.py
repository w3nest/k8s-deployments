from fastapi import APIRouter, Depends, Request
from kubernetes_asyncio import client as k8s_client

from w3nest_infrakube_backend.environment import (
    Configuration,
    Environment,
    format_entry_message,
    log_resp,
)

from .schemas import ServiceAccount, ServiceAccountList, TokenResponse

# Disable because falsy detection of code-duplication
# pylint: disable=duplicate-code
router = APIRouter()

TOPIC_ICON = "👤"


@router.get(
    "/contexts/{k8s_ctx}/namespaces/{namespace_name}/service-accounts",
    response_model=ServiceAccountList,
)
async def get_service_accounts(
    request: Request,
    k8s_ctx: str,
    namespace_name: str,
    config: Configuration = Depends(Environment.get_config),
) -> ServiceAccountList:

    async with config.context(request).start(
        action=format_entry_message(TOPIC_ICON, "List Service Accounts"),
        with_attributes={
            "k8s_ctx": k8s_ctx,
            "namespace_name": namespace_name,
        },
    ) as ctx:

        k8s_api = await Environment.get_k8s_api(k8s_ctx)
        v1 = k8s_client.CoreV1Api(k8s_api)
        service_accounts = await v1.list_namespaced_service_account(
            namespace=namespace_name
        )
        return await log_resp(
            ServiceAccountList.from_k8s(
                k8s_ctx=k8s_ctx, service_accounts=service_accounts
            ),
            ctx,
        )


@router.get(
    "/contexts/{k8s_ctx}/namespaces/{namespace_name}/service-accounts/{sa_name}",
    response_model=ServiceAccount,
)
async def get_service_account(
    request: Request,
    k8s_ctx: str,
    namespace_name: str,
    sa_name: str,
    config: Configuration = Depends(Environment.get_config),
) -> ServiceAccount:

    async with config.context(request).start(
        action=format_entry_message(TOPIC_ICON, "Get Service Account"),
        with_attributes={
            "k8s_ctx": k8s_ctx,
            "namespace_name": namespace_name,
            "sa_name": sa_name,
        },
    ) as ctx:

        k8s_api = await Environment.get_k8s_api(k8s_ctx)
        v1 = k8s_client.CoreV1Api(k8s_api)
        service_account = await v1.read_namespaced_service_account(
            name=sa_name, namespace=namespace_name
        )
        return await log_resp(
            ServiceAccount.from_k8s(k8s_ctx=k8s_ctx, service_account=service_account),
            ctx,
        )


@router.get(
    "/contexts/{k8s_ctx}/namespaces/{namespace_name}/service-accounts/{sa_name}/token"
)
async def get_service_account_token(
    request: Request,
    k8s_ctx: str,
    namespace_name: str,
    sa_name: str,
    config: Configuration = Depends(Environment.get_config),
) -> TokenResponse:

    async with config.context(request).start(
        action=format_entry_message(TOPIC_ICON, "Get Service Account Token"),
        with_attributes={
            "k8s_ctx": k8s_ctx,
            "namespace_name": namespace_name,
            "sa_name": sa_name,
        },
    ):

        k8s_api = await Environment.get_k8s_api(k8s_ctx)
        v1 = k8s_client.CoreV1Api(k8s_api)

        token_request = k8s_client.AuthenticationV1TokenRequest(
            spec=k8s_client.V1TokenRequestSpec(
                audiences=["https://kubernetes.default.svc.cluster.local"],
                expiration_seconds=3600,
            )
        )
        token_response = await v1.create_namespaced_service_account_token(
            name=sa_name, namespace=namespace_name, body=token_request
        )

        return TokenResponse.from_k8s(k8s_ctx=k8s_ctx, token=token_response)
