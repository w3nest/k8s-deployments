from w3nest_infrakube_backend.routers.config_maps.router import (
    router as config_maps_router,
)
from w3nest_infrakube_backend.routers.contexts.router import router as contexts_router
from w3nest_infrakube_backend.routers.ingresses.router import router as ingresses_router
from w3nest_infrakube_backend.routers.logs.router import router as logs_router
from w3nest_infrakube_backend.routers.namespaces.router import (
    router as namespaces_router,
)
from w3nest_infrakube_backend.routers.nodes.router import router as nodes_router
from w3nest_infrakube_backend.routers.persistent_volumes.router import (
    router as pv_router,
)
from w3nest_infrakube_backend.routers.pods.router import router as pods_router
from w3nest_infrakube_backend.routers.secrets.router import router as secrets_router
from w3nest_infrakube_backend.routers.service_accounts.router import (
    router as service_accounts_router,
)
from w3nest_infrakube_backend.routers.services.router import router as services_router
from w3nest_infrakube_backend.routers.w3nest.router import router as w3nest_router
