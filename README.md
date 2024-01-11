# ReportHub from iMMAP

Staging app: [Staging demo](https://dev.reporthub.immap.org/)

Documentation: [Technical Documentation](https://immap.github.io/rh/)


## Setup the project locally

## Using Docker
Build the containers
```shell
make run-dependencies
```

**Run Command in the containers**
```shell
# Django app
docker-compose -f docker-compose.dev.yml run --rm django make serve
docker-compose -f docker-compose.dev.yml run --rm django make migrate
docker-compose -f docker-compose.dev.yml run --rm django make migrations

# Vite app on the static
docker-compose -f docker-compose.dev.yml run --rm npm make vite-host
docker-compose -f docker-compose.dev.yml run --rm --service-ports make vite-host
#
docker-compose -f docker-compose.dev.yml run --rm npm make npm-install
docker-compose -f docker-compose.dev.yml run --rm npm make npm-build
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