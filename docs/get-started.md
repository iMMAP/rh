# Setup the project locally

Clone the project
```shell
git clone https://github.com/iMMAP/rh.git
```

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

### Use data from CSV file
Beside using fake data you can also use the data provided in the csv files.
```shell
cd scripts

python migrate_mongodb.py
```

The above script will add data from CSV files to your sqlite database.

## Check code with linter and formatter
```shell
make lint
```
[Ruff](https://github.com/astral-sh/ruff) is used for linting and formatting.

Ruff is an extremely fast Python linter and code formatter.
It can replace Flake8 and black formatter.
Install the vs code extension to setup immediatly.


