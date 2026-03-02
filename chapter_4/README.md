# Chapter 4 - Running Integration Tests in GitHub Actions

In this chapter, you will configure GitHub Actions to automatically run the integration tests for the project located in the folder chapter_4.

### Learning objectives

By the end of this chapter, you will:
- Understand what a GitHub Actions workflow is
- Create a workflow file from scratch
- Run a job on an Ubuntu runner
- Install Python in CI
- Install a Python project located in a subfolder
- Execute integration tests using pytest
- Debug common CI issues

### Project structure
The Python project and integration tests are located inside:
```
chapter_4/
  pyproject.toml
  ...
```
Your workflow must execute commands inside this folder.

## The task 

Create a workflow that:
1. Can be run manually from GitHub and can also be called from another workflow.
2. Runs on `ubuntu-latest` 
3. Installs Python 3.13.
4. Installs the project inside chapter_4/ 
5. Runs the integration tests using `pytest`.

## Task 1: Create the Workflow File

Create a new file `.github/workflows/integration-tests.yml` and, in that file, start by giving the workflow a name, for example `name: Run integration tests`.

### Task 2: Make It Runnable from GitHub

Add a manual trigger so we can start it from the GitHub UI:

```
on:
  workflow_dispatch:
    inputs:
      lane:
        description: "Target environment"
        required: true
        type: string
        default: 'development'
```

After committing this, you should see a Run workflow button in the Actions tab.

You can also add a wokflow_call so that you can run this workflow from other workflows you implement in the future.
```
workflow_call:
    inputs:
      lane:
        description: "Target environment"
        required: true
        type: string
        default: 'development'
```
### Task 3: Add permissions to your workflow
```
permissions:
  contents: read
```

### Task 4: Configure Environment Variables
The integration tests expect a database connection string via `TICKETS_DATABASE_URL` Set this environment variable in your workflow, the value should be `postgresql+psycopg://train:train@db:5432/train`.

### Task 5: Define a Job

Create a job named tests that runs on Ubuntu:
```
jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
```

This means that Github will provision a fresh Ubuntu machine where nothing is pre-installed except OS and basic tooling.

The runner starts empty so we need to set up a list of steps that run subsequencially.

#### Step 1: Checkout the repository

The runner starts empty so your code does not exist there until you download it.

Add a step that checks out the repository using `actions/checkout@v4`. The structure is 
```
- name: Checkout repository
  uses: actions/checkout@v4
  with:
    repository: * Name of your repo *
    ref: * Nme of your branch * 
```

#### Step 2: Set up Python

To ensure that all participants run tests with the same interpreter, add a step that uses `actions/setup-python@v5`. The structure is 

```
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: * Pytohn version you are using *
```

#### Step 3: Install the project

```
- name: Install dependencies
  working-directory: * Directory of your project *
  run: |
    pip install -e ".[dev]"
```

**Hint**: If you run this in the wrong directory, pip will fail with: `neither setup.py nor pyproject.toml` found.

#### Step 4: Run the Integration Tests
```
- name: Run integration tests with pytest
  working-directory: * Directory of your project *
  run: |
    * Run command with pytest *
```

## Running the Workflow

1. Commit and push your changes to the main branch in your fork.
2. Go to the Actions tab in GitHub.
3. Select your workflow.
4. Click Run workflow.
5. Open the job logs to inspect each step.

## Reflection Questions

After completing the exercise, consider:
- Why do we explicitly install Python?
- Why must we checkout the repository?
- Why does CI not “remember” previous runs?
- What would happen if we removed -s?
