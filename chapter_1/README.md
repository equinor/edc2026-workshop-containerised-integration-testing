# Chapter 1 - The limits of unit-testing

## Preparing for the ride of your life

Every journey starts with buying a ticket! You wouldn't dare sneak onto the train without buying a ticket first? There
is no escape once the ticket inspector catches you!

Therefore, we have created an API which enables you to buy tickets. The Tickets API consists of a FastAPI application
and a corresponding database which is used to store the tickets. It has an endpoint for buying a ticket and an endpoint
for checking that the ticket is valid. Your task is to run the application and verify that it functions as expected once
it is placed in production.

The conductors have high expectations to quality and will not accept a ticket system which is not 100% reliable.

## Setup

Ensure you have a virtual environment installed for this specific chapter with python 3.13+. Recommendation is to create
it in this folder as there will be several venvs in different parts of the workshop. If you're not familiar with virtual
environments you will be at the end of this! Please ask for help if needed.

Create a virtual environment.

```
python -m venv venv
```

Activate your virtual environment.

```
source venv/bin/activate        # macOS / Linux

.\venv\Scripts\Activate.ps1     # Windows (PowerShell)
```

Install dependencies and the application itself.

```
pip install -e ".[dev]"
```

Please refer back to this section for future chapters where creating a virtual environment is required.

## Task 1: Run the application? Already? Have you verified that the tests pass?

As we are all good developers we know that tests come first. Always. Thus, we should ensure all the tests for our
application pass before we could ever think about running the application itself. Worst case scenario the API takes the
customers money without providing a valid ticket in return. The conductors would be furious!

Open a terminal and execute the tests.

````bash
pytest .
````

Familiarize yourself with the tests which have been created for our Tickets API. They can be found in the tests folder.

## Task 2: Run the application locally

The tests pass as expected, but you figure some additional manual testing wouldn't do any harm. Spin up the application
locally.

Run the following command:

```python main.py```

The swagger interface for the API can now be accessed at

```http://localhost:3000/docs```

There are two endpoints present in the interface.

```
/tickets/buy
/tickets/{ticket_id}
```

## Task 3: Verify your tests locally

As you fear the wrath of the conductors you elect to manually verify all the unit tests through manually testing in the
API. Maybe we should hire someone to deal with Quality Assurance for us?

There is one unit test in the tests folder (`test_buy_ticket`) which has three different inputs. Verify all three
manually using the Tickets API endpoints such that the conductors feel comfortable that everything is working as
expected. Every ticket you buy with the ``/tickets/buy`` endpoint can be verified by calling `/tickets/{ticket_id}` with
the ID provided by the response in the buy endpoint.

Do you get the same results as with the unit tests?

## Task 4: Run the application in production

Now that you know the tests pass, and it works locally you feel absolutely certain that the ticketing system can't steal
money without providing a valid ticket. Let's push the application to production so the conductors can be happy. To
simulate the production environment we will use Docker Compose.

Open a terminal and execute the following command. Ensure you have stopped the api running locally (as they share the
same port) and, if you are using Docker Desktop, you need to ensure the Docker Engine has been started by opening the
Docker Desktop application.

```docker compose up```

## Task 5: Verify tests in production

While you are absolutely certain you are also paranoid, having had horrible experiences with the conductors on your
latest release, and decide to perform the unit tests manually once more but now in the production environment.

Repeat the three manual tests from [Task 4](#task-4-verify-your-tests-locally) by using the test input values in the
endpoints. Do you get the same results as with the unit tests? If not, what is the cause?

## Task 6: How can we accurately test our production environment locally?

The functionality worked perfectly both in our unit tests and when performing manual QA locally.

- Have we tested enough?
- Have we tested correctly?
- How can we accurately emulate the production environment such that you can discover bugs before the conductors
  do?

Once you have considered please feel free to attempt the bonus task below until this section is discussed in plenary.

## Bonus task

The [docker-compose.yml](docker-compose.yml) file starts a postgres database which is used to store the tickets. It can
be useful to inspect the database to ensure it contains what you think it does. The
application [pgadmin4](https://www.pgadmin.org/) is excellent at connecting to the database and inspecting the different
tables.

Download the pgadmin4 tool (or use a different tool you are familiar with) to connect to the postgres database running
from our docker-compose file. Username and password for connecting to the database are given in the docker-compose.

Add some tickets using the API and observe them through the pgadmin4 tool. 