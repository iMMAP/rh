# ReportHub from iMMAP

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