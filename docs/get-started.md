# Setup the project locally
> Read the README.md of the repo

Clone the project
```shell
git clone https://github.com/iMMAP/rh.git
```

## Using Docker
Build the containers
```shell
make docker-up
```

## No Docker

### Install poetry
Make sure Poetry is installed on your machine
```shell
poetry --version
```

If not installed, install Poetry with:

```shell
pip install poetry
```

### Create a virtualenv 
```shell
virtualenv .venv
```

### Install the dependencies
Make sure to 'make' installed for your machine.

```shell
make install # to install python package
make npm-install # to install npm packges inside static folder
```

### Run the project:

Run Django development server
```shell
make serve
```
Run the vite developement server

```shell
make vite
```

## Seed the Database

### Generate fake data for testing
```shell
make seed
```
or 
```shell
poetry run python src/manage.py seed --amount 10
```
Will create fake data necessary for testing and starting out.
for more information check `src/rh/management/commands/seed.py` file.

## Check code with linter and formatter
```shell
make lint
```
[Ruff](https://github.com/astral-sh/ruff) is used for linting and formatting.

Ruff is an extremely fast Python linter and code formatter.
It can replace Flake8 and black formatter.
Install the vs code extension to setup immediatly.