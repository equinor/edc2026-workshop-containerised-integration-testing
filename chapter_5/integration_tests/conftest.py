import time
from datetime import datetime
from typing import Generator
from loguru import logger
from testcontainers.core.container import DockerContainer

import pytest

from integration_tests.custom_containers.postgres import (
    PostgresDatabase,
    create_postgres_container,
)
from integration_tests.custom_containers.tickets_api import TicketsAPI


@pytest.fixture
def tickets_api(postgres_database: PostgresDatabase) -> TicketsAPI:
    raise NotImplementedError


@pytest.fixture
def postgres_database() -> Generator[PostgresDatabase]:
    with create_postgres_container() as postgres:
        wait_for_port_mapping_to_be_available(container=postgres, port=5432)
        psql_url: str = postgres.get_connection_url()
        yield PostgresDatabase(
            container=postgres, connection_string=psql_url, alias=postgres.dbname
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
