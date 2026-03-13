import time
from datetime import datetime, timedelta
from typing import Dict

import requests
from loguru import logger
from requests import RequestException, Response
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network

from integration_tests_ch7.custom_containers.log_docker_container import (
    LogDockerContainer,
)


class TrainLogisticsAPI:
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


def create_train_logistics_api_container(
    network: Network,
    database_connection_string: str,
    azure_storage_connection_string: str,
) -> LogDockerContainer:
    container: LogDockerContainer = (
        LogDockerContainer(image="ghcr.io/equinor/train-logistics:latest")
        .with_exposed_ports(3001)
        .with_network_aliases("train_logistics_api")
        .with_network(network)
        .with_env("TRAIN_LOGISTICS_DATABASE_URL", database_connection_string)
        .with_env("AZURE_STORAGE_CONNECTION_STRING", azure_storage_connection_string)
    )

    return container


def wait_for_train_logistics_api_to_be_ready(
    backend_url: str, timeout: int = 20
) -> None:
    start_time: datetime = datetime.now()
    while True:
        if datetime.now() - start_time > timedelta(seconds=timeout):
            raise RuntimeError(
                f"Train Logistics API did not become ready within {timeout} seconds"
            )

        try:
            response: Dict = _get_health_endpoint(backend_url=backend_url)
        except RequestException:
            logger.warning("Train Logistics API is not ready yet, retrying...")
            time.sleep(1)
            continue

        if response.get("status") == "ok":
            logger.info("Train Logistics API is ready!")
            break

        time.sleep(1)


def _get_health_endpoint(backend_url: str) -> Dict:
    response: Response = requests.get(url=backend_url + "/openapi.json")
    response.raise_for_status()
    return {"status": "ok"}
