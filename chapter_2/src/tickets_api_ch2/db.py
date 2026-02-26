from datetime import datetime
from typing import Generator, Dict

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session
from sqlalchemy import String, Integer, create_engine, Engine, DateTime
from starlette.requests import Request


class Base(DeclarativeBase):
    pass


class Ticket(Base):
    __tablename__ = "ticket"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    train_code: Mapped[str] = mapped_column(String, nullable=False)
    passenger_name: Mapped[str] = mapped_column(String, nullable=False)
    seat_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    expiration_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)


def make_engine(database_url: str) -> Engine:
    connect_args: Dict = (
        {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    )
    return create_engine(database_url, connect_args=connect_args)


def make_sessionmaker(engine: Engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def create_tables(engine: Engine) -> None:
    Base.metadata.create_all(bind=engine)


def get_db(request: Request) -> Generator[Session, None, None]:
    session_local = request.app.state.session_local
    db = session_local()
    try:
        yield db
    finally:
        db.close()
