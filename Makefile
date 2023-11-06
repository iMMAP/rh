.PHONY: install
install:
	poetry install

.PHONY: install
test:
	poetry run python manage.py test

.PHONY: install-pre-commit
install-pre-commit:
	poetry run pre-commit uninstall && poetry run pre-commit install

.PHONY: lint
lint:
	poetry run pre-commit run --all-files

.PHONY: migrate
migrate:
	poetry run python manage.py migrate

.PHONY: migrations
migrations:
	poetry run python manage.py makemigrations

.PHONY: serve
serve:
	poetry run python manage.py runserver

.PHONY: vite
vite:
	cd static && npm run dev

.PHONY: npm-install
npm-install:
	cd static && npm install

.PHONY: superuser
superuser:
	poetry run python manage.py createsuperuser

.PHONY: update
update: install migrate install-pre-commit;
