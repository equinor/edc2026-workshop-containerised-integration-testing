import pytest

from fastapi.testclient import TestClient
from requests import Response

from tickets_api_ch2.models import TicketBuyRequest
from tickets_api_ch2.models import TicketDto


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
