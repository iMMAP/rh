# ReportHub from iMMAP

### Make sure Poetry is installed on your machine

```shell
poetry --version
```

If not installed, install Poetry with:

```shell
pip install poetry
```

### Install the dependencies

```shell
poetry install
```

### Run the project:

Run the Django server in local environment.

```shell
poetry run python manage.py runserver
```

Run the Django server in production environment.

```shell
poetry run python manage.py runserver --settings=core.settings.production
```

Run the vite asset bundler.

```shell
cd static && npm run dev
```

### Install additional package

```shell
poetry add package_name
```

### Install dev package

```shell
poetry add --dev package_name
```

### Update packages

```shell
poetry update
```

### Activate poetry virtual environment

```shell
poetry shell
```

### View dependencies tree

```shell
poetry show
```

## Production

Build the frontend assets

```shell
npm run build
```

## Use [ruff](https://github.com/astral-sh/ruff)

Install the vs code extension to setup immediatly.

An extremely fast Python linter and code formatter.
It can replace Flake8 and black formatter

## Using Flake8

Flake8 is a popular Python code linter, which is a tool that analyzes source code for potential errors, violations of coding conventions, and style inconsistencies. It combines multiple static analysis tools, including PyFlakes, pycodestyle (formerly known as pep8), and McCabe complexity checker.
Flake8 configuration is defined at the root level in the .flake8 file.

## To run Flake8

```shell
flake8
```
