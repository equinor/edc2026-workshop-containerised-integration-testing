from testcontainers.postgres import PostgresContainer


class PostgresDatabase:
    def __init__(self, container: PostgresContainer, connection_string: str, alias: str):
        self.container: PostgresContainer = container
        self.connection_string: str = connection_string
        self.alias: str = alias


def create_postgres_container() -> PostgresContainer:
    container: PostgresContainer = (
        PostgresContainer(
            image="postgres:17",
            username="train",
            password="train",
            dbname="train",
        )
        .with_name("train")
        .with_exposed_ports(5432)
    )

    return container