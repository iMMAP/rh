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

### 10. Star the server

```shell
python manage.py runserver
```
