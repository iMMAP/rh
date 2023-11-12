.PHONY: install
install:
	poetry install

.PHONY: install-pre-commit
install-pre-commit:
	poetry run pre-commit uninstall && poetry run pre-commit install

.PHONY: lint
lint:
	poetry run pre-commit run --all-files

.PHONY: migrate
migrate:
	poetry run python src/manage.py migrate

.PHONY: migrations
migrations:
	poetry run python src/manage.py makemigrations

.PHONY: serve
serve:
	poetry run python src/manage.py runserver

.PHONY: vite
vite:
	cd src/static && npm run dev

.PHONY: npm-install
npm-install:
	cd src/static && npm install

.PHONY: npm-build
npm-build:
	cd src/static && npm run build

.PHONY: superuser
superuser:
	poetry run python src/manage.py createsuperuser

.PHONY: update
update: install migrate install-pre-commit;

.PHONY: test
test:
	poetry run python src/manage.py test

.PHONY: db-seed
db-seed:
	poetry run python src/manage.py seed 

.PHONY: format-templates
	djlint --profile=django && djlint --reformat --profile=django
