import time
from datetime import datetime
from typing import Generator
from loguru import logger
from testcontainers.core.container import DockerContainer

import pytest
from testcontainers.core.network import Network

from chapter_7.integration_tests_ch7.custom_containers.azurite import (
    AzuriteStorageContainer,
    TrainLogisticsStorage,
    azurite_connection_string_for_containers,
    create_azurite_container,
    ensure_blob_containers,
)
from chapter_7.integration_tests_ch7.custom_containers.train_logistics import (
    TrainLogisticsAPI,
    create_train_logistics_api_container,
    wait_for_train_logistics_api_to_be_ready,
)
from integration_tests_ch7.custom_containers.postgres import (
    PostgresDatabase,
    create_postgres_container,
)
from integration_tests_ch7.custom_containers.tickets_api import (
    TicketsAPI,
    create_tickets_api_container,
    wait_for_tickets_api_to_be_ready,
)

AZURITE_ACCOUNT: str = "devstoreaccount1"
# Default Azurite development key — not a secret
AZURITE_KEY: str = (
    "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=="
)


@pytest.fixture
def network():
    with Network() as network:
        yield network


@pytest.fixture
def tickets_api(
    network: Network, postgres_database: PostgresDatabase
) -> Generator[TicketsAPI]:
    with create_tickets_api_container(
        network=network, database_connection_string=postgres_database.connection_string
    ) as container:
        wait_for_port_mapping_to_be_available(container=container, port=3000)
        backend_url: str = f"http://localhost:{container.get_exposed_port(3000)}"
        wait_for_tickets_api_to_be_ready(backend_url=backend_url)

        yield TicketsAPI(
            container=container,
            backend_url=backend_url,
            name="tickets_api",
            port=3000,
            alias="tickets_api",
        )


@pytest.fixture
def postgres_database(network: Network) -> Generator[PostgresDatabase]:
    network_alias: str = "postgres"

    with create_postgres_container(
        network=network, network_alias=network_alias
    ) as postgres:
        wait_for_port_mapping_to_be_available(container=postgres, port=5432)
        psql_url: str = (
            f"postgresql{postgres.driver}://{postgres.username}:{postgres.password}@{network_alias}:{postgres.port}/{postgres.dbname}"
        )
        yield PostgresDatabase(
            container=postgres, connection_string=psql_url, alias=network_alias
        )


def wait_for_port_mapping_to_be_available(
    container: DockerContainer, port: int, timeout: int = 60, delay: int = 2
) -> None:
    now: datetime = datetime.now()
    while (datetime.now() - now).seconds < timeout:
        try:
            container.get_exposed_port(port)
            return
        except ConnectionError:
            logger.warning(
                f"Port {port} not yet available, waiting for {delay} seconds..."
            )
            time.sleep(delay)
            continue

    raise ConnectionError(
        f"Port mapping for container {container.image} on port {port} not available within timeout"
    )


@pytest.fixture
def train_logistics_storage(
    network: Network,
) -> Generator[TrainLogisticsStorage, None, None]:
    raise NotImplementedError


@pytest.fixture
def train_logistics_api(
    network: Network,
    postgres_database: PostgresDatabase,
    train_logistics_storage: TrainLogisticsStorage,
) -> Generator[TrainLogisticsAPI]:
    raise NotImplementedError
