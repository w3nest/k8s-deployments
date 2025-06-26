import json

import aiohttp
from fastapi import APIRouter, Depends, Request

from w3nest_infrakube_backend.environment import (
    Configuration,
    Environment,
    format_entry_message,
)

LOKI_URL = "http://localhost:3100/loki/api/v1/query_range"

router = APIRouter()

TOPIC_ICON = "📋"


async def query_loki(namespace: str):
    # See [API documentation](https://grafana.com/docs/loki/latest/reference/loki-http-api/#stream-logs) and
    # [LogQL documentation](https://grafana.com/docs/loki/latest/query/)
    # curl -G http://localhost:3100/loki/api/v1/query --data-urlencode 'query={app="assets-gateway"}' | jq
    # curl -G ws://localhost:3100/loki/api/v1/tail --data-urlencode 'query={app="assets-gateway"}'
    query = f'{{namespace="{namespace}"}}'
    #  |= "{trace_id}"'
    params: dict[str, str] = {"query": query, "limit": "2000", "direction": "backward"}

    async with aiohttp.ClientSession() as session:
        async with session.get(LOKI_URL, params=params) as response:
            return await response.json()


def format_data(log):
    try:
        outer_json = json.loads(log)
        parsed = json.loads(outer_json["log"])
        return parsed
    except json.JSONDecodeError:
        return log


@router.get("/contexts/{k8s_ctx}/logs")
async def get_logs(
    request: Request,
    k8s_ctx: str,
    config: Configuration = Depends(Environment.get_config),
):
    async with config.context(request).start(
        action=format_entry_message(TOPIC_ICON, "Get Logs"),
        with_attributes={"k8s_ctx": k8s_ctx},
    ):
        logs = await query_loki(namespace="apps")
        results = [
            {"timestamp": ts, "data": format_data(data), "origin": r_pod["stream"]}
            for r_pod in logs["data"]["result"]
            for [ts, data] in r_pod["values"]
        ]
        return {"results": results}
