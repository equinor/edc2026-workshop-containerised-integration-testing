from testcontainers.core.container import DockerContainer


class TicketsAPI:
    def __init__(
        self,
        container: DockerContainer,
        backend_url: str,
        name: str,
        port: str,
        alias: str,
    ) -> None:
        self.container: DockerContainer = container
        self.backend_url: str = backend_url
        self.name: str = name
        self.port: str = port
        self.alias: str = alias


def create_tickets_api_container() -> DockerContainer:
    raise NotImplementedError
