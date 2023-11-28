# ReportHub from iMMAP

## Setup the project locally

### Using Docker
```shell
# Django app
docker-compose run --rm django make serve
docker-compose run --rm django make migrate
docker-compose run --rm django make migrations

# Vite app on the static
docker-compose run --rm npm make vite-host
docker-compose run --rm --service-ports make vite-host
#
docker-compose run --rm npm make npm-install
docker-compose run --rm npm make npm-build
```

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

### Run the linter
```shell
make lint
```

### Install additional package

```shell
poetry add package_name
```

### Install dev package

```shell
poetry add --dev package_name
```

### View dependencies tree

```shell
poetry show
```

## Production

Build the frontend assets

```shell
cd static && npm run build
```

## Linting and formatting 
[Ruff](https://github.com/astral-sh/ruff) is used for linting and formatting.

Ruff is an extremely fast Python linter and code formatter.
It can replace Flake8 and black formatter

Install the vs code extension to setup immediatly.



