import os

import uvicorn
from fastapi import FastAPI

from tickets_api.app import create_app


def start() -> None:
    database_url: str | None = os.getenv("TICKETS_DATABASE_URL")
    app: FastAPI = create_app(
        database_url=database_url if database_url else "sqlite:///train.db"
    )

    server: uvicorn.Server = _setup_server(app=app)
    server.run()


def _setup_server(app: FastAPI) -> uvicorn.Server:
    config = uvicorn.Config(app=app, port=3000, host="0.0.0.0", reload=False)
    return uvicorn.Server(config=config)


if __name__ == "__main__":
    start()
