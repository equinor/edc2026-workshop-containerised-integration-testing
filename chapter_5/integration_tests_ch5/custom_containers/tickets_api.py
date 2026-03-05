import time
from datetime import datetime, timedelta
from typing import Tuple, Dict

import requests
from loguru import logger
from requests import Response, RequestException
from testcontainers.core.container import DockerContainer
from testcontainers.core.image import DockerImage
from testcontainers.core.network import Network

from integration_tests.custom_containers.log_docker_container import LogDockerContainer


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


def create_tickets_api_container(
    network: Network,
    database_connection_string: str,
) -> Tuple[DockerImage, LogDockerContainer]:
    image: DockerImage = DockerImage(path="tickets_api", tag="tickets_api:latest")
    container: LogDockerContainer = (
        LogDockerContainer(image=str(image))
        .with_exposed_ports(3000)
        .with_network_aliases("tickets_api")
        .with_network(network)
        .with_env("TICKETS_DATABASE_URL", database_connection_string)
    )

    return image, container


def wait_for_tickets_api_to_be_ready(backend_url: str, timeout: int = 20) -> None:
    start_time: datetime = datetime.now()
    while True:
        if datetime.now() - start_time > timedelta(seconds=timeout):
            raise RuntimeError(
                f"Tickets API did not become ready within {timeout} seconds"
            )

        try:
            response: Dict = _get_health_endpoint(backend_url=backend_url)
        except RequestException:
            logger.warning("Tickets API is not ready yet, retrying...")
            time.sleep(1)
            continue

        if response.get("status") == "ok":
            logger.info("Tickets API is ready!")
            break

        time.sleep(1)


def _get_health_endpoint(backend_url: str) -> Dict:
    response: Response = requests.get(url=backend_url + "/health")
    return response.json()
