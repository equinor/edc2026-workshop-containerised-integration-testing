from tests.containers import PostgresDatabase

# Chapter 2 - Corporate needs you to find the differences between these pictures

![img.png](docs/corporate.png)

## NEVER AGAIN

Never again will you let a bug sneak past your testing routines to be discovered in the production environment. You will
not give those pesky conductors another chance to belittle you for faulty software. Having made your mind up you start
investigating how to improve your testing regime. As the last bug was caused by a database incompatibility where your
local SQLite database accepted something which your postgres database in production did not like you decide to focus on
that.

It's time to throw SQLite in the fire and run all your tests with the same database locally as you have in
production. But how can you run postgres efficiently in your local environment?

## Requirements to our local postgres database

During your research you set the following requirements to your local database.

- The database running with your unit tests must be the same as in production, postgres.
- You want a unique and empty database instance per test.
- You want the creation of new tests running with a database to be simple.
- You want the start and teardown of the database to be efficient.

After tedious research you settle on the [Testcontainers framework](https://testcontainers.com/?language=python) as a
suitable candidate.

## Setup

Create a new virtual environment for this chapter as you did in chapter 1. Ensure the new environment is activated in
your active terminal.

Install dependencies and the application itself.

```
pip install ".[dev]"
```

## Task 1: Creating a postgres database with Testcontainers

You immediately add the Testcontainers project to your dependencies in [pyproject.toml](./pyproject.toml) and decide to
spin up the postgres database. The conductors won't know what hit them (because no bugs will ever hit them again).

We implement the postgres database as a pytest fixture similarly to how we have the `database_url`, `app` and `client`
objects already implemented. The fixtures have now been moved to [conftest.py](./tests/conftest.py).

You assemble the skeleton for a new fixture in conftest.py. You also create a wrapper container class
`PostgresDatabase` which can hold your database in [containers.py](./tests/containers.py).

```python
# tests/conftest.py
@pytest.fixture
def postgres_database() -> Generator[PostgresDatabase]:
    # Implementation here
    yield PostgresDatabase(...)
```

```python
# tests/containers.py
class PostgresDatabase:
    def __init__(self, container: PostgresContainer, connection_string: str, alias: str):
        self.container: PostgresContainer = container
        self.connection_string: str = connection_string
        self.alias: str = alias
```

Using the official [testcontainers-python documentation](https://testcontainers-python.readthedocs.io/en/latest/),
[postgres community module documentation](https://testcontainers-python.readthedocs.io/en/latest/modules/postgres/README.html)
and your favorite AI model (or course instructor) your task is to create the `postgres_database` fixture which yields a
`Database`object.

### A note on `with` and `yield`

These keywords together are the key to efficient setup and teardown of your containers. The `with` statement defines the
lifetime of the container itself. When entering the `with` statement the container is created with all configuration
ensured. Once you exit the `with` statement the contianer is automatically torn down and removed from your system.

In the middle of this you have `yield`. It tells pytest where the setup and teardown of the fixture is. At the `yield`
statement pytest interprets this as "setup complete, now I can execute the test". Once the test has finished executing
pytest will return to the `yield` statement and continue execution. This leads to exiting the `with` statement and thus
the containers context manager tears down your containers safely.

## Task 2: Start the postgres container

Add another test in [test_ticket_system.py](./tests/test_ticket_system.py) which you can use to test if the container is
behaving as you expect it to.

```python
# tests/test_ticket_system.py
from loguru import logger


def test_start_postgres_container(postgres_database: PostgresDatabase) -> None:
    logger.info(f"Started database with name {postgres_database.container.dbname}")
    logger.info(f"Started database with image {postgres_database.container.image}")
    logger.info(f"Started database with username {postgres_database.container.username}")
    logger.info(f"Started database with password {postgres_database.container.password}")
    logger.info(f"Started database with port {postgres_database.container.port}")
    logger.info(f"Started database with connection string {postgres_database.connection_string}")
```

Execute that test while you observe your Docker Desktop GUI or monitor your containers live in the terminal with the
command `docker stats`. Does anything happen?

## Task 3: Configuring the container

Provided that your container started successfully, it's time to configure it. The default configuration can be seen as
the log output from your test. And while "test" is fair enough we are dealing with trains here! Your task is to
explicitly set the following configuration for the container.

```
image=postgres:17
username=train
password=train
dbname=train
port=5432
```

### Hint

Investigate the `PostgresContainer` class and parent classes until you find the `DockerContainer` class. Which fields
are available in these two classes? Which configuration options are available to you?

- Specifically look at the `def with_` functions which are very helpful for configuration.

## Task 4: Inspecting the container

Now it's time to remotely access the container (or maybe we should call it locally access?). There are multiple ways to
do this, particularly easy with Docker Desktop, but we will do it through the terminal.

First, ensure that your test `test_start_postgres_container` doesn't finish running. If it does the container will just
be torn down by the framework, and we won't have time to inspect it. Multiple ways to Rome, but either debug the test or
add an infinite while-loop.

Once your container is running for eternity, open a new terminal and run the following command to get a list of all
running containers.

```bash
docker ps       # add argument -a if you want to see stopped containers
```

Inspect the output and find the name for your container. It will be a randomly generated name, but you can see the image
is `postgres:17`.

The following command will allow you to open a bash terminal in the container. Replace `<container_name>` with the name
of your container.

```bash
docker exec -it <container_name> /bin/bash
```

Now you can inspect anything in the container. Did you add some files in your Dockerfile which it can't find? Wondering
if your environment variables have been correctly passed along? Being able to inspect the container is very useful to
debug and recognize what is wrong with your setup.

### The RYUK container

When checking for your container name you would have seen another container named "ryuk" running. This container is
managed by the Testcontainers framework and is responsible for monitoring and cleaning up any containers that are left
dangling after your tests. This is a safety mechanism to ensure that you don't end up with a lot of unused containers
taking up resources on your machine. Think of it as a container orchestrator which you do not have to think too much
about (unless you want to run tests in parallel).

## Task 5: Running our existing unit tests with the postgres database

Finally, we have come to running our existing unit test `test_buy_ticket` with the postgres database instead of the
in-memory SQLite database. The moment of truth has arrived.

The test is currently set up to run with the `database_url` fixture which is configured to use SQLite. Your task is to
change the fixtures such that the `app` fixture uses the `postgres_database` fixture instead of the `database_url`
fixture. Once complete, run the unit tests again.

### Hint

Your postgres connection string should have the following format where values are configurable but some examples can be
seen in [docker-compose.yml](./docker-compose.yml).

```python
connection_string: str = (
    f"Host={database_alias}; Port={5432}; Username={database_username}; Password={database_password}; "
    f"Database={database_alias}; SSL Mode=Disable;"
)
```

## Bonus tasks

### Exploring community modules

Postgres is available as a community module in Testcontainers which means you can use it out of the box (the
`PostgresContainer` object) without requiring further implementation on your side. There are many different applications
with an existing community module which means you can easily include them in your tests.

[List of testcontainers community modules](https://testcontainers-python.readthedocs.io/en/latest/modules/index.html)

See anything that would be useful for your projects? Anything missing?

### Connecting to your database with pgadmin4

Remember the bonus task in [Chapter 1](../chapter_1/README.md)? Here is your chance to connect to the postgres database
which is running in your test with Testcontainers.

#### Hint

Unless you pause the test somehow the container will simply be torn down by the Testcontainers framework before you can
inspect it. 