import subprocess
import base64
from pathlib import Path
from kubernetes_asyncio import client as k8s_client

from kubernetes_asyncio.client.api_client import ApiClient, Configuration
from kubernetes_asyncio import config as k8s_config

from kubernetes_asyncio.client import V1Secret


async def get_k8s_config(k8s_ctx: str) -> Configuration:

    k8s_configuration = k8s_client.Configuration()
    config_path = Path(k8s_config.KUBE_CONFIG_DEFAULT_LOCATION)

    # pylint: disable=protected-access
    loader = k8s_config.kube_config._get_kube_config_loader_for_yaml_file(
        filename=str(config_path),
        persist_config=True,
        active_context=k8s_ctx,
        temp_file_path=None,
    )

    await loader.load_and_set(k8s_configuration)
    return k8s_configuration


async def get_secret(
    k8s_config: Configuration,
    namespace_name: str,
    secret_name: str,
):
    async with ApiClient(configuration=k8s_config) as api:

        v1 = k8s_client.CoreV1Api(api)
        secret: V1Secret = await v1.read_namespaced_secret(
            name=secret_name, namespace=namespace_name
        )
        secret_data = {
            key: base64.b64decode(value).decode("utf-8")
            for key, value in secret.data.items()
        }
        return secret_data


async def port_fwd_service(
    k8s_config: Configuration, port: int, service: str, namespace: str
):

    async with ApiClient(configuration=k8s_config) as k8s_api:

        print(
            f"📡 Establishing port-forward of service '{namespace}:{service}' on port {port}..."
        )

        v1 = k8s_client.CoreV1Api(k8s_api)

        k8s_service = await v1.read_namespaced_service(
            name=service, namespace=namespace
        )
        if k8s_service.spec.ports:
            internal_port = k8s_service.spec.ports[0].port
            print(f"🔍 Found internal port {internal_port} for service '{service}'")
        else:
            raise ValueError(
                f"Service '{service}' in '{namespace}' has no defined ports"
            )

        command = [
            "kubectl",
            "port-forward",
            f"--namespace={namespace}",
            f"service/{service}",
            f"{port}:{internal_port}",
        ]

        # Run the command in the background
        subprocess.Popen(command)
