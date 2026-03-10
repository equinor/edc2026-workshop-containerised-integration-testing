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

TODO: Setup azurite container in the tests

## Task 3: Proper integration testing

TODO: Create an integration test which includes Azurite, Tickets API, Train Logistics&trade; and postgres.

Image: ![img.png](img.png)