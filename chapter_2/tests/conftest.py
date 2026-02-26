from pathlib import Path
from typing import Iterator, Generator

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from .containers import PostgresDatabase
from tickets_api_ch2.app import create_app


@pytest.fixture
def database_url(tmp_path: Path) -> str:
    return f"sqlite:///{tmp_path}/test.db"


@pytest.fixture
def app(database_url: str) -> FastAPI:
    return create_app(database_url=database_url)


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as client:
        yield client


@pytest.fixture
def postgres_database() -> Generator[PostgresDatabase]:
    raise NotImplementedError


