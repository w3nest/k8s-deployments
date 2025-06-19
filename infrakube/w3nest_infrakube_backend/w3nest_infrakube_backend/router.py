"""
Module gathering the definition of endpoints.
"""

from fastapi import APIRouter
from starlette.responses import Response

from w3nest_infrakube_backend.routers import (
    config_maps_router,
    contexts_router,
    ingresses_router,
    logs_router,
    namespaces_router,
    nodes_router,
    pods_router,
    pv_router,
    secrets_router,
    service_accounts_router,
    services_router,
    w3nest_router,
)

router = APIRouter()
"""
The global router object.
"""

router.include_router(contexts_router)
router.include_router(namespaces_router)
router.include_router(pods_router)
router.include_router(services_router)
router.include_router(secrets_router)
router.include_router(service_accounts_router)
router.include_router(ingresses_router)
router.include_router(nodes_router)
router.include_router(pv_router)
router.include_router(config_maps_router)
router.include_router(logs_router)
router.include_router(w3nest_router)


@router.get("/")
async def home():
    """
    When proxied through w3nest, this end point is always triggered when
    testing whether a backend is listening.
    """
    return Response(status_code=200)
