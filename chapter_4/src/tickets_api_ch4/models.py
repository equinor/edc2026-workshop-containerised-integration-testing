from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class TicketBuyRequest(BaseModel):
    train_code: str = Field(..., examples=["T1-OSL-TRD"])
    passenger_name: str = Field(..., examples=["Richard Trevithick"])
    seat_number: int | None = Field(..., examples=[12, None])


class TicketDto(BaseModel):
    id: int
    train_code: str
    passenger_name: str
    seat_number: int | None
    expiration_date: datetime
