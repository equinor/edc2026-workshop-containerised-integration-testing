# Chapter 7 - Train Logistics&trade;

The dreaded day has arrived. Your manager walked into the landscape today looking lost and confused, he sits on the 14th
floor of course, and pulled you aside to introduce this brand-new application requested by the conductors that will
solve all their problems. He then went into how important it would be for the company, how it would be a
game-changer for the industry and how fortunate you were that had been hand-picked to implement this project. When you
asked about the increased responsibility and effects on your salary, he merely laughed and went back to his office on
the 14th floor.

While you don't get a salary increase you have a certain professional integrity that you want to uphold, not to
mention an overshadowing fear of the conductors. But you have prepared for this moment and decide to implement some
basics and immediately get an integration test running!

## Setup

Same as always, create a new virtual environment for this chapter. Ensure the new environment is activated in
your active terminal.

Install dependencies and the application itself.

```
pip install ".[dev]"
```

## Task 1: The Train Logistics&trade; application

The application is another API which manages the logistics related operations of the trains. How much food is available
in the train for instance? The Train Logistics&trade; will be an amazing application which monitors all of this.

## Task 2: The storage solution

While your manager said "brand-new" it turns out you need to work with some legacy systems. The current system
uses JSON files which are stored in an Azure storage account to monitor the amount of available resources on the train.
The conductors have been very explicit in that they like this approach, it's so easy to just edit the files. Why would
you do anything else?

While clearly insane, you conclude that you need to support this JSON data input style for now. The application will
have to talk to Azure storage blobs. How can you keep going with the integration tests while having to interact with a
Microsoft service?

Fortunately, Microsoft has provided us with a gift: [Azurite](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azurite),
a local emulator for Azure Blob Storage. It runs as a Docker container which is exactly what we need.

The Azurite helper functions are already prepared for you in
[custom_containers/azurite.py](integration_tests_ch7/custom_containers/azurite.py). Take a moment to read through the
file and understand the three helpers:

- `create_azurite_container()` — spins up the Azurite image bound on `0.0.0.0` so Docker can expose its ports to the
  host. It accepts a `name` which doubles as the network alias.
- `azurite_connection_string_for_containers()` — builds the connection string. You will call this twice: once with the
  container alias (for container-to-container traffic on the Docker network) and once with `localhost` (for the host
  machine to seed data into the storage from within the fixture).
- `ensure_blob_containers()` — uses the host-side connection string to pre-create the blob containers before the Train
  Logistics API starts looking for them.

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

Keep `yield` **inside** the `with` block. If you place it outside, the context manager exits before your test runs,
the Azurite container is destroyed, the Train Logistics API cannot connect to storage, and you will spend a
very pleasant afternoon watching a retry loop print the same warning over and over again. You have been warned.

## Task 3: Proper integration testing

With Azurite in place you now have all four pillars ready to assemble into a proper multi-container integration test.

| Container             | Purpose                                       |
|-----------------------|-----------------------------------------------|
| `postgres`            | Shared database for both APIs                 |
| `tickets_api`         | The original ticketing application            |
| `train_logistics_api` | The new logistics application                 |
| `azurite`             | Azure Blob Storage emulator for JSON manifests |

Architecture overview:

Image: ![img.png](img.png)

### Task 3a: The Train Logistics&trade; fixture

The Train Logistics&trade; application lives in a remote repository and is published as a Docker image at
`ghcr.io/equinor/train-logistics:latest`, exactly like the Tickets API in chapter 6.

The helper functions `create_train_logistics_api_container()` and `wait_for_train_logistics_api_to_be_ready()` are
already implemented for you in
[custom_containers/train_logistics.py](integration_tests_ch7/custom_containers/train_logistics.py). Read through them.

The container exposes port `3001` and requires two environment variables which the factory function already wires up
for you:
- `TRAIN_LOGISTICS_DATABASE_URL` — the postgres connection string using the `postgres` network alias.
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

The `TrainLogisticsAPI` wrapper class (already defined in `train_logistics.py`) expects: `container`, `backend_url`,
`name`, `port`, and `alias`.

### Task 3b: Write the integration tests

Two tests need to be added to [test_integration.py](integration_tests_ch7/test_integration.py).

**`test_buy_ticket`** — a familiar face from chapter 5. Make a `POST` request to `/tickets/buy` on the `tickets_api`
container and verify the response body contains the expected fields.

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
    tickets_api: TicketsAPI,
    train_code: str,
    passenger_name: str,
    seat_number: str | int,
) -> None:
    ...
```

**`test_check_stock`** — the first test written against the Train Logistics&trade; API. Make a `POST` request to
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
congratulations. You have just run a four-container integration test from a single `pytest` command. No manual setup,
no shared cloud bill, no angry conductor breathing down your neck.

## Bonus task

You now have a working four-container integration test harness. Before moving on, consider the following:

- The `train_logistics_storage` fixture hardcodes the Azurite account name and key as local variables. Could you
  promote them to module-level constants to avoid repeating them if you add more Azurite fixtures later?
- The `if/elif` block checking `expected_in_stock` values in `test_check_stock` can be replaced entirely if you add
  `expected_in_stock` as a third parameter directly in the `parametrize` decorator. Is that cleaner?
- What would happen if you wanted to test against two separate Azurite instances for two different services? How would
  you extend the `TrainLogisticsStorage` class to support that?