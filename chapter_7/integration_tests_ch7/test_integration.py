from http import HTTPStatus
from typing import Dict

import pytest
import requests
from loguru import logger
from requests import Response

from chapter_7.integration_tests_ch7.custom_containers.azurite import (
    TrainLogisticsStorage,
)
from chapter_7.integration_tests_ch7.custom_containers.train_logistics import (
    TrainLogisticsAPI,
)
from integration_tests_ch7.custom_containers.postgres import PostgresDatabase
from integration_tests_ch7.custom_containers.tickets_api import TicketsAPI


def test_startup_of_custom_tickets_api_container(
    tickets_api: TicketsAPI,
    postgres_database: PostgresDatabase,
    train_logistics_storage: TrainLogisticsStorage,
    train_logistics_api: TrainLogisticsAPI,
) -> None:
    logger.info(f"Started Tickets API with image {tickets_api.container.image}")
    logger.info(f"Started Tickets API with port {tickets_api.port}")

    logger.info(f"Started database with name {postgres_database.container.dbname}")
    logger.info(
        f"Started database with username {postgres_database.container.username}"
    )
    logger.info(
        f"Started database with password {postgres_database.container.password}"
    )
    logger.info(f"Started database with port {postgres_database.container.port}")

    logger.info(
        f"Started train logistics storage with containers: {list(train_logistics_storage.azurite_containers.keys())}"
    )

    logger.info(
        f"Started train logistics API with image {train_logistics_api.container.image}"
    )
    logger.info(f"Started train logistics API with port {train_logistics_api.port}")


@pytest.mark.parametrize(
    "train_code,passenger_name,seat_number",
    [
        ("The Orient Express", "Leonardo DaVinci", 14),
        ("Bergensbanen", "Jonas Gahr Støre", 1),
        ("Raumabanen", "Kong Harald", None),
    ],
)
def test_buy_ticket(
    tickets_api: TicketsAPI,
    train_code: str,
    passenger_name: str,
    seat_number: str | int,
) -> None:
    payload: Dict = {
        "train_code": train_code,
        "passenger_name": passenger_name,
        "seat_number": seat_number,
    }
    url: str = f"{tickets_api.backend_url}/tickets/buy"

    response: Response = requests.post(url=url, json=payload)

    content: Dict = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert content["id"]
    assert content["train_code"] == train_code
    assert content["passenger_name"] == passenger_name
    assert content["seat_number"] == seat_number


@pytest.mark.parametrize(
    "train_code,product,expected_in_stock",
    [
        ("The Orient Express", "banana", 10),
        ("Bergensbanen", "apple", 5),
        ("Raumabanen", "orange", 0),
    ],
)
def test_check_stock(
    train_logistics_api: TrainLogisticsAPI,
    train_code: str,
    product: str,
    expected_in_stock: int,
) -> None:
    raise NotImplementedError
