import time
from datetime import datetime
from typing import Iterator, Generator

import pytest
from fastapi import FastAPI
from loguru import logger
from starlette.testclient import TestClient
from testcontainers.core.container import DockerContainer
from testcontainers.postgres import PostgresContainer

from .containers import PostgresDatabase
from tickets_api_ch3.app import create_app


@pytest.fixture
def app(postgres_database: PostgresDatabase) -> FastAPI:
    return create_app(database_url=postgres_database.connection_string)


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as client:
        yield client


@pytest.fixture
def postgres_database() -> Generator[PostgresDatabase]:
    with PostgresContainer(
        image="postgres:17",
        username="train",
        password="train",
        dbname="train",
        driver="psycopg",
    ).with_exposed_ports(5432) as postgres:
        wait_for_port_mapping_to_be_available(container=postgres, port=5432)

        psql_url: str = postgres.get_connection_url()
        yield PostgresDatabase(
            container=postgres, connection_string=psql_url, alias=postgres.dbname
        )


def wait_for_port_mapping_to_be_available(
    container: DockerContainer, port: int, timeout: int = 10, delay: int = 2
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
