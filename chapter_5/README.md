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

## Task 2: Inspecting the logs from your container

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

## Task 3: Networking

## Task 4: Write a test towards the Tickets API
