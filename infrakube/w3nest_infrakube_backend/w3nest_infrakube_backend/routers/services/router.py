import subprocess
from socket import AF_INET, SOCK_STREAM, socket
import time

from fastapi import APIRouter
from kubernetes_asyncio import client as k8s_client
from kubernetes_asyncio.client.api_client import ApiClient

from w3nest_infrakube_backend.environment import Environment

from .schemas import PortForwardBody, PortForwardResponse, Service, ServiceList

router = APIRouter()


@router.get(
    "/contexts/{k8s_ctx}/namespaces/{namespace_name}/services",
    response_model=ServiceList,
)
async def get_services(k8s_ctx: str, namespace_name: str) -> ServiceList:

    async with ApiClient(
        configuration=await Environment.get_k8s_config(k8s_ctx=k8s_ctx)
    ) as k8s_api:
        v1 = k8s_client.CoreV1Api(k8s_api)
        services = await v1.list_namespaced_service(namespace=namespace_name)
        return ServiceList.from_k8s(k8s_ctx=k8s_ctx, services=services)


@router.get(
    "/contexts/{k8s_ctx}/namespaces/{namespace_name}/services/{service_name}",
    response_model=Service,
)
async def get_service(
    k8s_ctx: str,
    namespace_name: str,
    service_name: str,
) -> Service:

    async with ApiClient(
        configuration=await Environment.get_k8s_config(k8s_ctx=k8s_ctx)
    ) as k8s_api:
        v1 = k8s_client.CoreV1Api(k8s_api)
        service = await v1.read_namespaced_service(
            name=service_name, namespace=namespace_name
        )
        label_selector = service.spec.selector
        label_selector_str = (
            ",".join([f"{key}={value}" for key, value in label_selector.items()])
            if label_selector
            else ""
        )

        pods = await v1.list_namespaced_pod(
            namespace=namespace_name, label_selector=label_selector_str
        )
        return Service.from_k8s(k8s_ctx=k8s_ctx, service=service, pods=pods.items)


def find_available_port(start: int, end: int) -> int:
    for port in range(start, end + 1):
        with socket(AF_INET, SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return port
            except OSError:
                continue
    # Raise an exception if no port is available
    raise RuntimeError(f"No available port found in the range {start}-{end}")


def wait_for_port(host: str, port: int, timeout: float = 10.0, delay: float = 0.2):
    """Wait until a TCP port is open on a host."""
    end_time = time.time() + timeout
    while time.time() < end_time:
        with socket(AF_INET, SOCK_STREAM) as sock:
            sock.settimeout(delay)
            try:
                sock.connect((host, port))
                return True
            except (ConnectionRefusedError, OSError):
                time.sleep(delay)
    raise TimeoutError(f"Port {port} on {host} did not open within {timeout} seconds.")


async def port_fwd(
    k8s_ctx: str, namespace_name: str, service_name: str, port: int | None = None
) -> PortForwardResponse:

    key = f"{k8s_ctx}#{namespace_name}#{port}"
    if key in Environment.port_fwds:
        port, pid = Environment.port_fwds[key]
        return PortForwardResponse(url=f"http://localhost:{port}", port=port, pid=pid)

    async with ApiClient(
        configuration=await Environment.get_k8s_config(k8s_ctx=k8s_ctx)
    ) as k8s_api:

        if not port:
            port = find_available_port(2000, 3000)

        v1 = k8s_client.CoreV1Api(k8s_api)
        service = await v1.read_namespaced_service(
            name=service_name, namespace=namespace_name
        )
        if service.spec.ports:
            internal_port = service.spec.ports[0].port
            print(f"Found internal port {internal_port} for service '{service_name}'")
        else:
            raise ValueError(
                f"Service {service_name} in namespace {namespace_name} has no defined ports"
            )

        command = [
            "kubectl",
            "port-forward",
            f"--namespace={namespace_name}",
            f"service/{service_name}",
            f"{port}:{internal_port}",
            f"--context={k8s_ctx}",
        ]

        # Run the command in the background
        process = subprocess.Popen(command)
        print(f"⏳ Wait for port-forward on '{service_name} -> localhost:{port}'")
        wait_for_port("localhost", port)
        print(f"✅ Port forward listening\n")
        Environment.port_fwds[key] = (port, process.pid)
        return PortForwardResponse(
            port=port, url=f"http://localhost:{port}", pid=process.pid
        )


@router.post(
    "/contexts/{k8s_ctx}/namespaces/{namespace_name}/services/{service_name}/port-forward",
    response_model=PortForwardResponse,
)
async def port_forward_ep(
    k8s_ctx: str,
    namespace_name: str,
    service_name: str,
    body: PortForwardBody,
) -> PortForwardResponse:

    return await port_fwd(
        k8s_ctx=k8s_ctx,
        namespace_name=namespace_name,
        service_name=service_name,
        port=body.port,
    )
