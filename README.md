# ReportHub from iMMAP

Staging app: [Staging demo](https://dev.reporthub.immap.org/)

Documentation: [Technical Documentation](https://immap.github.io/rh/)


## Setup the project locally
### Clone the repo
```shell
git clone https://github.com/iMMAP/rh.git
```

#### Create a virtualenv 
```shell
cd rh

virtualenv .venv
# OR
python -m venv .venv
```

### Activate virtualenv
```shell
source ./.venv/bin/activate
```

#### Install poetry
install Poetry with:
```shell
pip install poetry
```

#### Create env file 
Create `.env` file by copying the sample file and update the values.
```shell
cp .env.sample .env
```

#### Install the dependencies
Make sure 'make' is installed for your machine.

```shell
make install # to install python package
make npm-install # to install npm packges inside static folder
make migrate

# Adds default db data
make seed # migrate_mongodb.py and load_activities
```

#### Run the project:

Run Django development server
```shell
make serve

make serve env=local
make serve env=production
```
Run the vite developement server

```shell
make vite
```

#### Run the linter
```shell
make lint
```

### Using Docker
#### Build the containers
```shell
make run-dependencies
```

### Management
[Management](https://immap.github.io/rh/Models/management)

#### Run Command in the containers
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

