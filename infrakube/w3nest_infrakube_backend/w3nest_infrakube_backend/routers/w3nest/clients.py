from w3nest_client import AioHttpExecutor
from w3nest_client.http.explorer import ExplorerClient

from w3nest_infrakube_backend.routers.services.router import (
    port_fwd,
)


async def explorer_client(
    k8s_ctx: str, request_executor: AioHttpExecutor
) -> ExplorerClient:

    print(f"✅ Successfully retrieved K8s configuration for context '{k8s_ctx}'")

    port_fwd_resp = await port_fwd(
        k8s_ctx=k8s_ctx, namespace_name="apps", service_name="explorer"
    )

    explorer = ExplorerClient(
        url_base=f"http://localhost:{port_fwd_resp.port}/api/explorer",
        request_executor=request_executor,
    )

    return explorer
