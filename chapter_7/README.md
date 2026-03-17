# Chapter 7 - Train Logistics&trade;

The dreaded day has arrived. Your manager walked into the landscape today looking lost and confused, he sits on the 14th
floor of course, and pulled you aside to introduce this brand-new application requested by the conductors that will
solve all their problems. He then went into how important it would be for the company, how it would be a game-changer
for the industry and how fortunate you were that had been hand-picked to implement this project. When you asked about
the increased responsibility and effects on your salary, he merely laughed and went back to his office on the 14th
floor.

While you don't get a salary increase you have a certain professional integrity that you want to uphold, not to mention
an overshadowing fear of the conductors. But you have prepared for this moment and decide to implement some basics and
immediately get an integration test running!

## Setup

Same as always, create a new virtual environment for this chapter. Ensure the new environment is activated in your
active terminal.

Install dependencies and the application itself.

```
pip install ".[dev]"
```

## Task 1: The Train Logistics application

The application is another API which manages the logistics related operations of the trains. How much food is available
in the train for instance? The Train Logistics&trade; will be an amazing application which monitors all of this.

Before writing a single line of test code, take a moment to understand what you are dealing with. The Train Logistics
API lives in its own remote repository and is published as a Docker image at `ghcr.io/equinor/train-logistics`, exactly
as the Tickets API was in chapter 6. It is not a standalone service, but depends on an Azure Blob Storage account. Your
task for now is simply to understand what the application needs before we dive into some implementation in task 2.

## Task 2: The storage solution

While your manager said "brand-new" it turns out you need to work with some legacy systems. The current system uses JSON
files which are stored in an Azure storage account to monitor the amount of available resources on the train.
The conductors have been very explicit in that they like this approach, it's so easy to just edit the files. Why would
you do anything else?

While clearly insane, you conclude that you need to support this JSON data input style for now. The application will
have to talk to Azure storage blobs. How can you keep going with the integration tests while having to interact with a
Microsoft service?

Fortunately, Microsoft has provided us with a
gift: [Azurite](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azurite), a local emulator for Azure
Blob Storage. It runs as a Docker container which is exactly what we need.

The Azurite helper functions are already prepared for you in
[custom_containers/azurite.py](integration_tests_ch7/custom_containers/azurite.py). Take a moment to read through the
file and understand the three helpers:

- `create_azurite_container()` — spins up the Azurite image bound on `0.0.0.0` so Docker can expose its ports to the
  host. It accepts a `name` which doubles as the network alias.
- `azurite_connection_string_for_containers()` — builds the connection string. You will call this twice: once with the
  container alias (for container-to-container traffic on the Docker network) and once with `localhost` (for the host
  machine to seed data into the storage from within the fixture).
- `ensure_blob_containers()` — uses the host-side connection string to pre-create the blob containers before the Train
  Logistics&trade; API starts looking for them.

Your task is to implement a `train_logistics_storage` fixture in
[conftest.py](integration_tests_ch7/conftest.py). The skeleton below shows where to start.

```python
# conftest.py
@pytest.fixture
def train_logistics_storage(network: Network) -> Generator[TrainLogisticsStorage, None, None]:
    azurite_container_name = "train-logistics"
    AZURITE_ACCOUNT: str = "devstoreaccount1"
    AZURITE_KEY: str = "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=="

    with create_azurite_container(network=network, name=azurite_container_name) as container:
        # 1. Wait for the port mapping to be available (port 10000)
        # 2. Build docker_connection_string using azurite_container_name as host
        # 3. Build host_connection_string using "localhost" and the exposed port
        # 4. Call ensure_blob_containers with the host connection string
        # 5. Yield a TrainLogisticsStorage with an AzuriteStorageContainer inside
        ...
```

> **Note on the Azurite credentials:** the account name and key above are the publicly documented defaults shipped with
> every Azurite installation. They are not secrets — you will find them in the official Microsoft documentation and in
> every tutorial on the internet. Do not lose sleep over them.

### The most important thing you will read in this chapter

Keep `yield` **inside** the `with` block. If you place it outside, the context manager exits before your test runs, the
Azurite container is destroyed, the Train Logistics&trade; API cannot connect to storage, and you will spend a very
pleasant afternoon watching a retry loop print the same warning over and over again. You have been warned.

## Task 3: Integration tests for the Train Logistics&trade; API and storage solution

### Task 3a: The Train Logistics&trade; fixture

The Train Logistics&trade; application lives in a remote repository and is published as a Docker image at
`ghcr.io/equinor/train-logistics:latest`, exactly like the Tickets API in chapter 6.

The helper functions `create_train_logistics_api_container()` and `wait_for_train_logistics_api_to_be_ready()` are
already implemented for you in
[custom_containers/train_logistics.py](integration_tests_ch7/custom_containers/train_logistics.py). Read through them.

The container exposes port `3001` and requires two environment variables which the factory function already wires up for
you:

- `AZURE_STORAGE_CONNECTION_STRING` — the Azurite connection string, **docker-side** (using the container alias, not
  `localhost`).

Your task is to add the `train_logistics_api` fixture in [conftest.py](integration_tests_ch7/conftest.py):

```python
# conftest.py
@pytest.fixture
def train_logistics_api(
        network: Network,
        postgres_database: PostgresDatabase,
        train_logistics_storage: TrainLogisticsStorage,
) -> Generator[TrainLogisticsAPI]:
    # 1. Get the docker-side connection string for Azurite from train_logistics_storage
    # 2. Start the container using create_train_logistics_api_container()
    # 3. Wait for port 3001 mapping, build backend_url
    # 4. Wait for the API to be ready using wait_for_train_logistics_api_to_be_ready()
    # 5. Yield a TrainLogisticsAPI object
    ...
```

The `TrainLogisticsAPI` wrapper class (already defined in `train_logistics.py`) expects `container`, `backend_url`,
`name`, `port`, and `alias`.

### Task 3b: Write the integration tests

A test needs to be added to [test_integration.py](integration_tests_ch7/test_integration.py). The `test_check_stock`
test is the first test written against the Train Logistics&trade; API. Make a `POST` request to
`/logistics/check-stock` with a `train_code` and `product` and assert the response contains the correct stock level.
This endpoint returns `200 OK` — it queries stock, it does not create anything. Do not assert `201 CREATED` unless you
enjoy failing tests.

```python
@pytest.mark.parametrize(
    "train_code,product,expected_in_stock",
    [
        ("The Orient Express", "banana", 10),
        ("Bergensbanen", "apple", 5),
        ("Raumabanen", "orange", 0),
    ],
)
def test_check_stock(
        train_logistics_api: TrainLogisticsAPI,
        train_code: str,
        product: str,
        expected_in_stock: int,
) -> None:
    ...
```

Run all tests with:

```bash
pytest -s .
```

If all four containers start, Azurite seeds correctly, both APIs accept requests and all assertions pass —
congratulations. You have just run a four-container integration test from a single `pytest` command. No manual setup, no
shared cloud bill, no angry conductor breathing down your neck.

## Task 4: Integration between the two APIs

Where task 3 still only allowed you to run two tests which were independent of each other, and did not interact
in-between the two APIs, we will now write a larger scale test. As you may have noticed earlier, there is an endpoint in
the Tickets API
for [counting the number of passengers on a train](https://github.com/equinor/tickets-api/blob/64e229f9d8ecaa2f5a619b46cee6ed1c372620ca/src/tickets_api/app.py#L91-L96).
Additionally, in the Train Logistics&trade; API, there
is
an [endpoint for buying new stock](https://github.com/equinor/train-logistics/blob/dc61d8818b42909146392350e71d07487fb4f407/src/train_logistics/app.py#L74-L116)
for a train. Have a look and notice that the logistics application asks the Tickets API for the number of passengers on
the trains and uses this to automatically refill the stock on the train.

Your manager comes running down from the 14th floor to show you the following picture.

![img.png](img.png)

It turns out a conductor managed to input "bandana" instead of "banana" in the JSON file, which caused the automatic
purchase of "bandanas". While the conductors enjoy their new look, management is furious about the overspending on new
inappropriate uniforms. You wonder who works in the purchasing department at the train company, as they clearly went
ahead and bought the bandanas without question. Not to mention the "I told you so" feeling you have about the insane
JSON file input approach which has caused this entire mess.

You reassure your manager that you are already working on a short-term remedial solution, integration testing, while
hinting at the need for a larger budget to remove the JSON input file.

Your task is to write an integration test which uses both the Tickets API and the Train Logistics&trade; API, with
corresponding storage solutions for both, that tests the above scenario. For now, it is enough that the tests runs with
the "bandana" scenario. How would you go about changing the Train Logistics&trade; API to ensure this does not happen
again?

### Hint

This task is deliberately left quite open. If stuck, please ask an instructor. 