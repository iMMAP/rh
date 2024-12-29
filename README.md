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

#### Create .env file 
Create `.env` file by copying the sample file and update the values.
```shell
cp .env.sample .env
```

### Generate secrete key
```shell
python src/manage.py generate_secret_key
```
Copy the output of the above command and update the `SECRET_KEY` variable in `.env` file

#### Install the dependencies
Make sure 'make' is installed for your machine.

```shell
# to install python package
make install

# to install npm packges for compling sass and etc
make npm-install 

# Run the migrations
make migrate
```

### Populate Initial Data
Populat the database with necessary data to start testing
```shell
# Adds default db data for testing
# The below command loads django fixtures data which is located in each django app. 
# rh/fixtures/<data>.json
make loaddata
```

#### Run the project:

Run Django development server
The `dev` command will run a django dev sever and vite server in the same terminal.
```shell
make dev
```

Or launch them separately
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
To check for linting erros and style formatting with ruff
```shell
make lint
```

### Using Docker
#### Build the containers
Build and run docker images
```shell
# docker compose up -d --build
make docker-up 
```

#### Run Command in the containers
```shell
# Django app
docker exec -it django bash
docker compose run --rm django make loaddata
```

### Platform Management
[Management](https://immap.github.io/rh/Models/management)