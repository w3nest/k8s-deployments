from fastapi import APIRouter
from kubernetes_asyncio import client as k8s_client
from kubernetes_asyncio.client.api_client import ApiClient

from w3nest_infrakube_backend.environment import Environment

from .schemas import ServiceAccount, ServiceAccountList, TokenResponse

# Disable because falsy detection of code-duplication
# pylint: disable=duplicate-code
router = APIRouter()


@router.get(
    "/contexts/{k8s_ctx}/namespaces/{namespace_name}/service-accounts",
    response_model=ServiceAccountList,
)
async def get_service_accounts(
    k8s_ctx: str,
    namespace_name: str,
) -> ServiceAccountList:

    async with ApiClient(
        configuration=await Environment.get_k8s_config(k8s_ctx=k8s_ctx)
    ) as api:

        v1 = k8s_client.CoreV1Api(api)
        service_accounts = await v1.list_namespaced_service_account(
            namespace=namespace_name
        )
        return ServiceAccountList.from_k8s(
            k8s_ctx=k8s_ctx, service_accounts=service_accounts
        )


@router.get(
    "/contexts/{k8s_ctx}/namespaces/{namespace_name}/service-accounts/{sa_name}",
    response_model=ServiceAccount,
)
async def get_service_account(
    k8s_ctx: str,
    namespace_name: str,
    sa_name: str,
) -> ServiceAccount:

    async with ApiClient(
        configuration=await Environment.get_k8s_config(k8s_ctx=k8s_ctx)
    ) as api:

        v1 = k8s_client.CoreV1Api(api)
        service_account = await v1.read_namespaced_service_account(
            name=sa_name, namespace=namespace_name
        )
        return ServiceAccount.from_k8s(k8s_ctx=k8s_ctx, service_account=service_account)


@router.get(
    "/contexts/{k8s_ctx}/namespaces/{namespace_name}/service-accounts/{sa_name}/token"
)
async def get_service_account_token(
    k8s_ctx: str,
    namespace_name: str,
    sa_name: str,
) -> TokenResponse:

    async with ApiClient(
        configuration=await Environment.get_k8s_config(k8s_ctx=k8s_ctx)
    ) as api:

        v1 = k8s_client.CoreV1Api(api)

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
