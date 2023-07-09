# ReportHub from iMMAP

## Quick Setup

### 1. Install the latest version of python and virtualenv or virtualenvwrapper.

```
virtualenv installation:
https://virtualenv.pypa.io/en/latest/installation.html
```

### 2. Clone this repository

```
git clone git@github.com:iMMAP/rh.git
```

### 3. Create virtualenv environment

```shell
cd rh
virtualenv --python=<YOUR_LOCAL_PYTHON_PATH> .venv

# or if you are using virtualenvwrapper

mkvirtualenv reporthub

```

### 4. Activate your environment

```shell
source .venv/bin/activate

# or if you are using virtualenvwrapper

workon reporthub
```

### 5. Install packages

```
pip install -r requirements_dev.txt
```

### 6. Create .env file

Copy `.env.sample` file and rename it to `.env`

```
cp .env.sample .env
```

### 7. Create a secret key

Run the bellow command and copy the result to SECRET_KEY in .env file

```shell
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

```

### 8. Run the migrations

```shell
python manage.py migrate
```

### 9. Create a super user

```shell
python manage.py createsuperuser
```

### 10. Start the server

```shell
python manage.py runserver
```

## How to use Poetry 

### Make sure Poetry is installed on your machine 

```commandline
poetry --version
```

If not installed,  install Poetry with: 

```commandline
pip install poetry
```

### Install the dependencies

```commandline
poetry install
```

###Run the project: 

```commandline
poetry run python manage.py runserver
```

### Install additional package 
```commandline
poetry add package_name
```

### Install dev package 
```commandline
poetry add --dev package_name
```

### Update packages

```commandline
poetry update
```
### Activate poetry virtual environment

```commandline
poetry shell    
```

### View dependencies tree

```commandline
poetry show
```

## Using Flake8

Flake8 is a popular Python code linter, which is a tool that analyzes source code for potential errors, violations of coding conventions, and style inconsistencies. It combines multiple static analysis tools, including PyFlakes, pycodestyle (formerly known as pep8), and McCabe complexity checker.
Flake8 configuration is defined at the root level in the .flake8 file. 

## To run Flake8

```commandline
flake8
```