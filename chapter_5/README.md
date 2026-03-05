# Chapter 5 - Increasing the complexity

Rumours are circulating in the corridors at Train Software HQ that the conductors have demanded a brand-new application
for managing Train Logistics. The Train Logistics&trade; application will manage re-supply for the Trains at different
train stations and will need to communicate with the Tickets API to know how many passengers are on the train to make
informed decisions.

Once the project comes trickling down the chain of command you know it will be handed to you with a "please fix this"
note. But you have developed since the Tickets API first saw its first dawn. You will be ready, you will have a test
suite which smoothly integrates into the new application, where you can test both applications together! Yes, you will
have integration tests! The other developers (in your head) give you a standing ovation for the rousing speech.

## Setup

The layout of the project has changed a bit since you last saw it in chapter 4. The `tickets_api` is now in a folder of
its own, while we have made a new python package named `integration_tests`. We will now work mainly in the
`integration_tests` package while the `tickets_api` package will be used to build a docker image which allows us to run
the Tickets API.

Same as always, create a new virtual environment for this chapter. Ensure the new environment is activated in
your active terminal.

Install dependencies and the application itself. Note that we are now installing the `integration_tests` package.

```
pip install ".[dev]"
```

## Task 1: The custom container

To be prepared for integration tests from day one on the new application you must first create a setup that easily
allows you to run your full Tickets API in a test with the future Train Logistics&trade; application. You will do this
by creating a custom container that runs the Tickets API and can be used in the integration tests for the Train
Logistics&trade; application.

Your task is to create a custom container for the Tickets API which runs in a Testcontainer. We will then create
brand-new tests which are not limited to interacting with the Tickets API through the `TestClient`, but which interact
with the full application running in a Testcontainer instead.

Start by inspecting the [core documentation](https://testcontainers-python.readthedocs.io/en/latest/core/README.html)
for the Testcontainers library in python. The example usage of the `DockerImage` and `DockerContainer`classes should get
you started. Note that we have now packed the `tickets_api` into a folder of its own. You will not run the API directly
from the source code, but instead build a docker image from the `tickets_api` folder and interact with that container.

The test you can run can be seen in [test_integration.py](./integration_tests/test_integration.py), and you need
to define fixtures for the custom container in [conftest.py](./integration_tests/conftest.py). The custom container
itself should be defined
in [integration_tests/custom_containers/tickets_api.py](./integration_tests/custom_containers/tickets_api.py) where we
have also defined a wrapper class similarly to what we did with the database. Note that we have already defined the
postgres database fixture in [conftest.py](./integration_tests/conftest.py), with a slightly different setup than before
where the container itself is created in a function
in [custom_containers/postgres.py](./integration_tests/custom_containers/postgres.py).

When running the tests now position yourself in the `chapter_5` folder and use the command `pytest`. We have configured
the test run inside the `pyproject.toml`file.

### Hint

#### Environment variables for custom containers

The Tickets API was designed to take the database connection string as an environment variable `TICKETS_DATABASE_URL`.
Investigate the `.with_env()` function in the `DockerContainer` class to set the environment variable.

#### Image versus container

The image must be available before you can start the container. Thus keep in mind that you have to enter a context
manager for the image first before doing the same for the container.

## Task 2: More waiting

When creating your custom container in task 1 you might have included the `wait_for_port_mapping_to_be_available`
function as part of the fixture to ensure the container is ready before you continue with your testing. Working with
containers it's good practice to ensure everything is ready before moving on.

Is this enough?

There is a difference between the statements "the container is ready" and "the application inside the container is
ready". The `wait_for_port_mapping_to_be_available` function only waits for the container to be ready, but it does not
ensure the Fast API application in Tickets API has actually started. Our tests will execute immediately when our waiting
strategies have come to an end. If the application has not started by then, our tests will fail. This is a common issue
when working with Testcontainers and Docker in general, and it's something you need to be aware of.

Your task is to write another wait function which should this time ensure the application has started.

### Hint

There are several ways you can do this. We previously mentioned the `wait_for_logs` function which may be used here.
However, we prefer to poll the API and wait for a valid response from an endpoint. To facilitate, we have added a
`/health` endpoint to the API which makes a simple request to the database to ensure everything is ready. It can be
found in [app.py](./tickets_api/app.py).

## Task 3: Inspecting the logs from your container

If task 1 went as expected you will see the log statements from the test in your terminal. However, there are no
logs from inside the container itself. If the container works perfectly you might not bother too much, but the instant
it fails to start for some reason it would be so good to get the logs. Not to mention if the test fails. As this is not
built-in functionality we here create a helper class which allows us to enable passing all our container
logs to the test output. It makes our life easier.

Inspect the `LogDockerContainer` class
in [integration_tests/custom_containers/log_docker_container.py](./integration_tests/custom_containers/log_docker_container.py).
This is a wrapper around the `DockerContainer` class which allows us to pass the logs from the container to the test
output. The `LogDockerContainer` class is then used as a base class for the `TicketsApiContainer`.

Your task is to edit the custom container you created in task 1 to inherit from `LogDockerContainer` instead of
`DockerContainer`. This will allow you to see the logs from the container in your test output, which is very useful for
debugging when something goes wrong.

First, run the `test_startup_of_custom_tickets_api_container` as in the previous task. You must now run it with the
command `pytest -s` as this disables output capture and sends logs to your terminal immediately. What do you see?

Then, add a small sleep at the end of the test. What do you see now? Is the Tickets API working as you expect? If not,
jump straight to Task 3 to understand why! If it actually works we have a problem.

```python
import time

time.sleep(5)
```

### Hint

The `LogDockerContainer` class is somewhat complex, and we do not want to focus too much on the details in the workshop
as it's not the core purpose here. Suffice it to say that there could be many ways of achieving this result, and here we
have chosen to attach another thread which is responsible for capturing the log output of the container and forwarding
it to our test output. Additionally, we have some logic to ensure the thread and container is correctly disposed.

## Task 4: Networking

As you hopefully saw in the previous task, our Tickets API failed to connect to the database. The obvious culprit was
the following line in the error output.

```bash
2026-03-04 12:46:58.174 | INFO     | custom_containers.log_docker_container:_stream_logs:61 - None: sqlalchemy.exc.OperationalError: (psycopg.OperationalError) failed to resolve host 'postgres': [Errno -2] Name or service not known
```

Why? Because of the way Docker networking works. Previously, when we were using our postgres database to run unit tests,
we were operating by running our tests from the host machine towards a Docker container which had mapped its ports to
`localhost`. Now we are attempting to make two separate docker containers talk together which has nothing to do with the
host machine.

If you inspect the `create_postgres_container()` function
in [custom_containers/postgres.py](./integration_tests/custom_containers/postgres.py) you will see that we have already
made some changes in this chapter which incorporates parts of this. The network alias has been added for our postgres
container such that on the docker network you may use `postgres` instead of `localhost` or an IP address. We have also
adjusted the connection string such that it now points to an address internally on the Docker Network.

First, do the same to your `create_tickets_api_container()` function and ensure it adds an alias to our tickets_api
container as well. Use `tickets_api` as your alias.

Now, you are going to ensure all your containers are on the same Docker Network such that they can talk to each other.
Testcontainers comes with a `Network` module which is not mentioned a lot in the documentation, but here is
the [source file](https://github.com/testcontainers/testcontainers-python/blob/main/core/testcontainers/core/network.py)
which may be used for reference.

Add a new fixture to `conftest.py` which introduces a network as shown below.

```python
import pytest
from testcontainers.core.network import Network


@pytest.fixture
def network():
    with Network() as network:
        yield network
```

Then, your task is to ensure this fixture is propagated to both the postgres and tickets_api containers and that they
are configured with the correct network.

Once you have configured all containers to use the same network, attempt to run the test again with the sleep active. Is
there a difference to the log output?

### Hint

Those useful `.with_` configuration functions again...

## Task 5: Write a test towards the Tickets API

Finally, we have a functioning setup where we can run the full Tickets API as a custom container which is also able to
talk to our database. All running in docker and started through pytest. To finish it off, lets write a proper test, not
just the one we have now that is for show.

Going all the way back to chapter one, implement the following test, except now we make calls to the Tickets API running
in our container instead of the `TestClient`.

```python
@pytest.mark.parametrize(
    "train_code,passenger_name,seat_number",
    [
        ("The Orient Express", "Leonardo DaVinci", 14),
        ("Bergensbanen", "Jonas Gahr Støre", 1),
        ("Raumabanen", "Kong Harald", None),
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
```

### Hint

While we do have access to the `tickets_api` package here, we have not installed it, and it would be better to make our
tests independent of the package itself. Use a library for requests, e.g. the requests library, and verify the response
content you receive from the API.

## Bonus task

The foundations are in place. Before we extend even further with more components and remote repositories, take a moment
to consider how this functionality could be used in your applications. 