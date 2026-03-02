# Chapter 3 - Wait for it...

Having fixed your unit tests to fail when they should fail (hopefully) you feel better about your situation with the
nasty conductors. However, paranoia is harder to fix than failing unit tests so you decide to embark on extending your
test suite with more complex unit tests which could uncover any bug. But you encounter some issues...

## Setup

Create a new virtual environment for this chapter as you did in chapter 1. Ensure the new environment is activated in
your active terminal.

Install dependencies and the application itself.

```
pip install ".[dev]"
```

## Task 1: When has a container started? When is it ready?

A new test has been added to your test suite `test_start_postgres_container_and_access_exposed_ports`. This test starts
the container and immediately attempts to access the exposed port. The exposed port is the port which port 5432 on the
container is mapped to on the host machine. We have enabled this behavior by `with_exposed_port(5432)` command when
setting up the container itself.

Run the test and observe the behavior. Does it pass?

### Hint

It may pass or may not pass. From our experience this is a timing issue that will sometimes arise, particularly when you
are working with custom containers. Suffice it to say that the container may be running but the service inside the
container may not be ready to accept connections yet. This is a common issue when working with containers and is often a
source of annoyance when performing setup.

## Task 2: How to wait for a container to be ready?

While you may not have been able to notice an issue in the previous task, it is likely that you will encounter it later
so we present a method of avoiding the issue. This method is general and will be extensively used later to ensure
different parts of the integration tests are ready before we can start our tests.

Your task is to implement the following function which can be found in `conftest.py`.

```python
def wait_for_port_mapping_to_be_available(
        container: DockerContainer, port: int, timeout: int = 10, delay: int = 2
) -> None:
    # Implementation of wait for port mapping to be available
    raise NotImplementedError
```

Once implemented, incorporate it into your `postgres_database` fixture to ensure the database is ready before you start
your tests.

### Hint

The container will throw an exception of type `ConnectionError` when you attempt to access the exposed port
before the service inside the container is ready.

## Task 3: Waiting for an API

If you were to run your Tickets API as a custom container (foreshadowing), how would you implement a wait strategy to
ensure the API is ready before starting your test? Consider your method, which we will come back to later, and then move
on to the next chapter.

## Bonus task

### Waiting for logs

In some cases, it may be useful to wait for a specific log message to appear in the container logs before proceeding
with the test. This can be particularly useful when waiting for an application to start up and become ready to accept
requests. There is built-in functionality in Testcontainers to wait for log messages. Have a look at the [core
documentation](https://testcontainers-python.readthedocs.io/en/latest/core/README.html) to learn how this can be done
with the `wait_for_logs` method. 