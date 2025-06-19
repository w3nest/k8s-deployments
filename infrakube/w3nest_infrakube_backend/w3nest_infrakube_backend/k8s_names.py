from typing import NamedTuple


class IngressesNames(NamedTuple):
    dashboard: str = "dashboard"
    assets_gtw: str = "assets-gateway"


class Names(NamedTuple):
    ingresses: IngressesNames = IngressesNames()
