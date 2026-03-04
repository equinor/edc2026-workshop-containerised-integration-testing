from typing import Tuple

from testcontainers.core.container import DockerContainer
from testcontainers.core.image import DockerImage


class TicketsAPI:
    def __init__(
        self,
        container: DockerContainer,
        backend_url: str,
        name: str,
        port: int,
        alias: str,
    ) -> None:
        self.container: DockerContainer = container
        self.backend_url: str = backend_url
        self.name: str = name
        self.port: int = port
        self.alias: str = alias


def create_tickets_api_container() -> Tuple[DockerImage, DockerContainer]:
    raise NotImplementedError
