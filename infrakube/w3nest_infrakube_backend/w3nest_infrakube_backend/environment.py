"""
Module gathering elements regarding the configuration of the server.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeVar

from kubernetes_asyncio import client as k8s_client
from kubernetes_asyncio import config as k8s_config
from kubernetes_asyncio.client.api_client import ApiClient
from starlette.requests import Request
from w3nest_client import BaseModel, Context, ContextFactory
from w3nest_client.context.models import ProxiedBackendCtxEnv

from w3nest_infrakube_backend.k8s_names import Names


@dataclass(frozen=True)
class Configuration:
    """
    Holds configuration fields.
    """

    host: str
    """
    Server's host.
    """
    port: int
    """
    Server's port.
    """
    host_port: int
    """
    Host's port.
    """
    host_name: str
    """
    Host's name.
    """
    instance_name: str
    """
    Instance name.
    """
    log_level: str | int | None
    """
    Uvicorn log level.
    """

    def __str__(self):
        """
        Returns a string representation of the configuration.

        """
        return (
            f"Serving instance '{self.instance_name}' at '{self.host}:{self.port}', "
            f"connected to W3Nest host at '{self.host_name}:{self.host_port}'"
        )

    def context(self, request: Request) -> Context[ProxiedBackendCtxEnv]:
        """
        Returns an instance of context given an incoming request.
        It provides:
        *  Access to logging methods (`info`, `warning`, etc.) along with trace management.
        *  Access to W3Nest HTTP clients through its `.env` attribute.

        Parameters:
            request: Incoming request.

        Return:
            The context.
        """
        return ContextFactory.proxied_backend_context(
            request=request, host_url=f"http://{self.host_name}:{self.host_port}"
        )


class Environment:
    """
    Static class representing the running environment.
    """

    configuration: Configuration | None = None
    """
    Configuration instance.
    """
    config_path: Path = Path(k8s_config.KUBE_CONFIG_DEFAULT_LOCATION)

    k8s_configs: dict[str, Any] = {}

    k8s_api_store: dict[str, ApiClient] = {}

    k8s_names = Names()

    port_fwds: dict[str, tuple[int, int]] = {}
    """
    Key is K8S_CTX@NAMESPACE@SERVICE, value is (port, process id)
    """

    @staticmethod
    def get_config():
        """
        Retrieves the configuration instance.
        It is injected in the various endpoints as a FastAPI dependency.
        """
        if not Environment.configuration:
            raise RuntimeError(
                "Configuration instance must be set before being accessed"
            )
        return Environment.configuration

    @staticmethod
    def set_config(configuration: Configuration):
        """
        Set the configuration singleton.
        """
        if Environment.configuration:
            raise RuntimeError("Configuration instance can only be set once.")
        Environment.configuration = configuration

    auth_timestamp: float

    @staticmethod
    async def get_k8s_config(k8s_ctx: str):

        if k8s_ctx in Environment.k8s_configs:
            return Environment.k8s_configs[k8s_ctx]

        k8s_configuration = k8s_client.Configuration()
        # pylint: disable=protected-access
        loader = k8s_config.kube_config._get_kube_config_loader_for_yaml_file(
            filename=str(Environment.config_path),
            persist_config=True,
            active_context=k8s_ctx,
            temp_file_path=None,
        )

        await loader.load_and_set(k8s_configuration)
        Environment.k8s_configs[k8s_ctx] = k8s_configuration
        return k8s_configuration

    @staticmethod
    async def get_k8s_api(k8s_ctx: str):
        if k8s_ctx in Environment.k8s_api_store:
            return Environment.k8s_api_store[k8s_ctx]

        k8s_api = ApiClient(
            configuration=await Environment.get_k8s_config(k8s_ctx=k8s_ctx)
        )
        # pylint: disable=C2801
        Environment.k8s_api_store[k8s_ctx] = await k8s_api.__aenter__()
        return Environment.k8s_api_store[k8s_ctx]

    @staticmethod
    async def clear():
        for v in Environment.k8s_api_store.values():
            await v.close()


def format_entry_message(icon: str, message: str) -> str:
    return f"{icon} **{message}**"


T = TypeVar("T", bound=BaseModel)


async def log_resp(resp: T, ctx: Context) -> T:
    await ctx.info("Response", data=resp)
    return resp
