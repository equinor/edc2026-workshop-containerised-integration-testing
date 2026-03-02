from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from loguru import logger
from sqlalchemy import Engine

from tickets_api_ch4.db import create_tables, get_db, Ticket
from tickets_api_ch4.models import TicketBuyRequest, TicketDto

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from tickets_api_ch4.db import make_engine, make_sessionmaker


def create_app(database_url: str) -> FastAPI:
    engine: Engine = make_engine(database_url=database_url)
    session_local = make_sessionmaker(engine=engine)

    @asynccontextmanager
    async def lifespan(fast_api_app: FastAPI):
        fast_api_app.state.engine = engine
        fast_api_app.state.session_local = session_local
        create_tables(engine=engine)
        yield

    app: FastAPI = FastAPI(title="Train Ticketing API", lifespan=lifespan)

    @app.post("/tickets/buy", response_model=TicketDto, status_code=201)
    def buy_ticket(
        payload: TicketBuyRequest, db: Session = Depends(get_db)
    ) -> TicketDto:
        ticket: Ticket = Ticket(
            train_code=payload.train_code,
            passenger_name=payload.passenger_name,
            seat_number=payload.seat_number,
            expiration_date=datetime.now() + timedelta(hours=1),
        )

        db.add(ticket)
        try:
            db.commit()
        except SQLAlchemyError:
            db.rollback()

            error_description: str = (
                f"Failed to purchase ticket for train {ticket.train_code}, "
                f"passenger {ticket.passenger_name}, seat {ticket.seat_number}"
            )
            logger.exception(error_description)
            raise HTTPException(status_code=500, detail=error_description)

        db.refresh(ticket)

        return TicketDto(
            id=ticket.id,
            train_code=ticket.train_code,
            passenger_name=ticket.passenger_name,
            seat_number=ticket.seat_number,
            expiration_date=ticket.expiration_date,
        )

    @app.get("/tickets/{ticket_id}", response_model=TicketDto)
    def check_ticket(ticket_id: int, db: Session = Depends(get_db)) -> TicketDto:
        ticket: Ticket | None = db.get(Ticket, ticket_id)
        if ticket is None:
            error_description: str = f"Failed to find ticket with id {ticket_id}"
            logger.error(error_description)
            raise HTTPException(status_code=404, detail=error_description)

        if ticket.expiration_date < datetime.now():
            error_description: str = (
                f"Ticket {ticket_id} has expired, please buy a new ticket"
            )
            logger.error(error_description)
            raise HTTPException(status_code=409, detail=error_description)

        return TicketDto(
            id=ticket.id,
            train_code=ticket.train_code,
            passenger_name=ticket.passenger_name,
            seat_number=ticket.seat_number,
            expiration_date=ticket.expiration_date,
        )

    return app
