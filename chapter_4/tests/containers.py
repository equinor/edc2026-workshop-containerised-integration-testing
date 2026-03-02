from testcontainers.postgres import PostgresContainer


class PostgresDatabase:
    def __init__(self, container: PostgresContainer, connection_string: str, alias: str):
        self.container: PostgresContainer = container
        self.connection_string: str = connection_string
        self.alias: str = alias


