# Chapter 6 -

The hallway chatter about the Train Logistics&trade; application is increasing, and you can feel the deadline for
having your integration test setup approaching. Having achieved the basics in chapter 5, enabling you to test with the
Tickets API, you realize there is no reason to have the Tickets API with your integration tests. The packaging in
chapter 5 feels strange, and it would make more sense to separate the two. No mono-repo today.

You decide to split the Tickets API into a separate repository, which is also what you will do with the Train
Logistics&trade; application. Finally, you can have your integration tests in its own repository as well, and you can
have a clean separation of concerns.

## Setup

Once again, the layout of the project has changed. The `tickets_api` is now gone and the `integration_tests` package is
the sole survivor. This repository is from here on out solely concerned with orchestrating integration tests while our
application software and dependencies lives elsewhere.

Same as always, create a new virtual environment for this chapter. Ensure the new environment is activated in
your active terminal.

Install dependencies and the application itself.

```
pip install ".[dev]"
```

## Task 1: Where did the Tickets API go?

The Tickets API is now in its own repository, and you can find it [here](https://github.com/equinor/tickets-api). The
repository contains the same code as before and there is not much different apart from modularization. There is however
one major change we have made which will allow us to run our integration tests still.

In the previous chapter, the custom container for the Tickets API was built using the Testcontainers `DockerImage`
class. Now that we have moved the context away from our local repository we must either fetch the remote repository or
build the docker image elsewhere. The [tickets-api repository](https://github.com/equinor/tickets-api) has a published
package which is created automatically on new releases. This is done
by [this workflow](https://github.com/equinor/tickets-api/blob/main/.github/workflows/publish_docker_image.yml).

The workflow publishes the package to the GitHub Container Registry. This works well, particularly open source as we are
now, but you can also use it for private repositories or decide to host your own container registry.

Your task is to update the fixture for our custom Tickets API container to use the remotely published docker image on
GitHub Container Registry instead of building it locally. Once you have done so, ensure all the tests pass by running
`pytest -s`.

### Discussion: Where do we actually run the integration tests?

In the end, your project is what determines where you would like them to run. There are several options. You could have
a repository for just the integrations tests and run them there. We have opted away from this as we prefer our tests
running close to our actual code. It is also difficult to have the integration tests as a check in your pull requests if
you do this.

Alternatively, we could move back to having the Tickets API in this repository and run the tests within the same
repository. What about when we get the new Train Logistics&trade; application? We would have to go monorepo or have
separate implementations of the integration tests in every repository. Monorepo is an option, just not our preferred one
and thus not covered here.

Finally, and the solution we have opted for, is to have the integration test repository define a reusable workflow
which every repository we have can import and execute as a local workflow.

## Task 2: Reusable workflows

Note, you have to be working on a fork for this task to work.

We have prepared a reusable workflow which is defined in [
.github/workflows/run_integration_tests_ch6.yml](.github/workflows/run_integration_tests_ch6.yml). Move the workflow
into the root folder `.github/workflows` folder which you most likely have after chapter 4. If not, create it.

Make sure you change the github username to you own (reflecting your fork) in the following section of the workflow.

```
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          repository: <your-github-username>/edc2026-workshop-containerised-integration-testing
          ref: main
```

Now push the workflow to your forks main branch, either directly or by creating a pull request from the branch you are
working on.

Go to the "Actions" tab on your forks github page and verify that the "Run integration tests chapter 6" workflow is
present. There should be a button "Run workflow" which you can use to run the test. Use "latest" as lane input.
![img.png](docs/img.png)

Does your workflow run successfully?

### Discussion: The lane input

If you inspect the workflow you will see that the lane input is currently not used for anything. This is true, but we
have included it to showcase a point. What if you have different environments and you build a docker image per
environment? This is true for our applications. When pushing to the main branch we build a dev image which we tag with
`:dev`. When creating a new release we build an image which we tag with `:latest`. This allows us to test against the
dev image in our pull requests and then test against the latest image when merging to main. The lane input is a way to
control which image we want to test against.

If you want to see an exact example have a look at
our [integration test workflow](https://github.com/equinor/armada/blob/main/.github/workflows/run_integration_tests.yml)
in the armada repository.

## Task 3: Remote execution of workflow

Now, we will execute the workflow in task 2 remotely from the Tickets API repository. Fork
the [tickets-api repository](https://github.com/equinor/tickets-api) and clone it to your local machine. You will not
need to create a virtual environment or install anything. In this repository there already exists a `.github/workflows`
folder as we had to build and publish the docker image from task 1.

Copy the example workflow we have given
in [.github/workflows/execute_integration_tests_remotely.yml](.github/workflows/execute_integration_tests_remotely.yml)
into the`.github/workflows` folder in your fork of the Tickets API repository. Ensure you change the username again to
reflect your fork of the workshop repository. Once done, push the changes to the main branch of your Tickets API fork.

Go to the "Actions" tab on your Tickets API fork and verify that the "Execute integration tests chapter 6" workflow is
present. Use the "Run workflow" button to run the workflow. Use "latest" as lane input.

### Discussion: Testing on pull request with different image tags

Once finished with this task you will be rewarded with the dopamine only a green checkmark can
give. ![img.png](docs/img_dopamine.png)

This is now running on every push to the main branch. We would ideally like to have it running on every pull request as
well, which we can easily do by setting the following in our workflow. If you wish to try it, go ahead!

```
on:
  push:
    branches: [ main ]
  release:
    types: [ published ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:
    inputs:
      lane:
        description: "dev or latest"
        required: true
        default: latest
```

One thing to consider is what happens when the system is complex, multiple repositories are involved and you have
different images. For example, on a pull request you might want to run towards the `:latest` images in other
repositories while doing `:dev` for you current repository as the `:latest` tag will only be built after the pull
request. We have plans to solve this but haven't got around to it yet.

### Discussion: Limitations of remote execution in public vs internal/private repositories

The remote execution of workflows is a neat feature which allows us to trigger our integration tests from the
repositories of our applications while only having to maintain the integrations tests themselves in one common location.
The common location can then orchestrate and import images from our different applications and dependencies.

However, due to corporate policy, it is not allowed to execute an internal workflow from a public repository. This means
that if your integration tests repository is internal, but you would like to run it from some repositories that are open
source, this is disabled. GitHub allows it, but corporate policy does not, which is fair. You are allowed to run
internal workflows from internal repositories.

Keep this in mind when designing your integration tests and considering the architecture. 