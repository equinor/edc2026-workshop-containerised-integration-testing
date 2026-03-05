import time
from http import HTTPStatus
from typing import Dict

import pytest
import requests
from loguru import logger
from requests import Response

from integration_tests_ch5.custom_containers.postgres import PostgresDatabase
from integration_tests_ch5.custom_containers.tickets_api import TicketsAPI


def test_startup_of_custom_tickets_api_container(
    tickets_api: TicketsAPI, postgres_database: PostgresDatabase
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

    time.sleep(5)


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
