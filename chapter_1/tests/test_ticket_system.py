from pathlib import Path
from typing import Iterator

import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from requests import Response

from tickets_api_ch1.app import create_app
from tickets_api_ch1.models import TicketBuyRequest
from tickets_api_ch1.models import TicketDto


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


@pytest.mark.parametrize(
    "train_code,passenger_name,seat_number",
    [
        ("The Orient Express", "Leonardo DaVinci", 14),
        ("Bergensbanen", "Jonas Gahr Støre", 1),
        ("Raumabanen", "Kong Harald", "unknown"),
    ],
)
def test_buy_ticket(
    client: TestClient, train_code: str, passenger_name: str, seat_number: str | int
) -> None:
    buy_ticket_payload: TicketBuyRequest = TicketBuyRequest(
        train_code=train_code,
        passenger_name=passenger_name,
        seat_number=seat_number,
    )

    buy_ticket_response: Response = client.post(
        "/tickets/buy/", json=buy_ticket_payload.model_dump()
    )
    ticket: TicketDto = TicketDto.model_validate(buy_ticket_response.json())

    assert ticket.id
    assert ticket.train_code == train_code
    assert ticket.passenger_name == passenger_name
    assert ticket.seat_number == seat_number
