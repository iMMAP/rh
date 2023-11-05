# ReportHub from iMMAP

### Make sure Poetry is installed on your machine

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



