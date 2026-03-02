# Chapter 4 - Running the integration tests in GitHub Actions (CI)

This repository includes a GitHub Actions workflow that automatically runs the integration tests on GitHub’s hosted runners. The goal is to reproduce the same “run tests from a clean machine” setup every time, without needing anything installed locally.

## Where the workflow lives

The workflow is defined as a YAML file under:

`.github/workflows/...`

When you push code to GitHub, GitHub scans that folder and runs workflows when their triggers match (for example: on every push, or when opening a pull request).

## When this workflow runs

### 1. Manually from the Github UI
```
on:
  workflow_dispatch:
```
This enables a Run workflow button in the Actions tab of your GitHub repository. When you click it, you can provide an input called `lane `(default has been set to `development`).

### 3. Called from another workflow (reusable workflow)
```
on:
  workflow_call:
```
This means another workflow in the same org/repo can call this workflow and pass the same lane input. This is useful when you want one central “test workflow” reused by multiple pipelines.

## Permissions 

```
permissions:
  contents: read
```
This is a minimal permission you can set, the workflow can read the repository contents, but can’t push or modify repo contents.

## Environment variables
```
env:
  TICKETS_DATABASE_URL: postgresql+psycopg://train:train@db:5432/train
```
This defines an environment variable available to all steps in the workflow. In the case of our example we only need one env variable. 

## What this workflow does?

On each run, the workflow:
1. Checks out the workshop project code into the runner
2. Sets up Python (so we control the Python version)
3. Installs the project and test dependencies
4. Runs pytest to execute the integration tests

This is the same sequence you’d do locally but executed on a clean GitHub machine.

## Step-by-step: what each step does

### 1. Checkout repository
```
- name: Checkout repository
  uses: actions/checkout@v4
  with:
    repository: equinor/edc2026-workshop-containerised-integration-testing
    ref: main
    path: .
```
This step clones the repository `main` branch into the Github runner filesystem. We also checkout into the root of the workspace($GITHUB_WORKSPACE) by setting `path: .`.

### 2. Set up Python
```
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: "3.13"
```
Installs and activates Python 3.13 so you get a consistent runtime across machines and participants.

### 3. Install dependencies 
```
- name: Install dependencies
  working-directory: chapter_4
  run: |
    pip install -e .
```

This runs `pip install -e .` inside chapter_4. `working-directory: chapter_4` is equivalent to doing `cd chapter_4` before running the command.
`-e .` installs the Python project in “editable mode”, which is useful for development/test scenarios.

Important requirement: the folder chapter_4 must contain a pyproject.toml or setup.py, otherwise pip will fail.

### 4. Run the integration tests
```
- name: Run integration tests with pytest
  working-directory: chapter_4
  run: |
    pytest -s .
```
This runs pytest inside the folder chapter_4. `-s` prints/logs the output in the GitHub Actions logs (good for learning/debugging).
