.PHONY: help
help:
	@echo "Available commands:"
	@grep -E '^\.\PHONY: ' $(MAKEFILE_LIST) | sed 's/\.PHONY: //; s/^/  /'

.PHONY: install
install:
	poetry install --no-root

.PHONY: install-no-dev
install-no-dev:
	poetry install --without dev

.PHONY: lint
lint:
	ruff check --output-format=github ./src
	ruff format ./src
	ruff check --select I --fix

.PHONY: migrate
migrate:
	poetry run python src/manage.py migrate

.PHONY: migrations
migrations:
	poetry run python src/manage.py makemigrations

env ?= local
.PHONY: serve
serve:
	poetry run python src/manage.py runserver --setting=core.settings.$(env)

.PHONY: vite
vite:
	npm run watch

.PHONY: dev
dev:
	make -j3 serve vite

.PHONY: npm-install
npm-install:
	npm install

.PHONY: npm-build
npm-build:
	npm run build

.PHONY: superuser
superuser:
	poetry run python src/manage.py createsuperuser

.PHONY: update
update: install migrate npm-install npm-build;

.PHONY: test
test:
	poetry run python src/manage.py test src

.PHONY: db-seed
db-seed:
	poetry run python src/manage.py seed

.PHONY: format-templates
format-templates:
	djlint --reformat --profile=django src

.PHONY: lint-templates
lint-templates:
	djlint --profile=django src

settings ?= core.settings.local 
.PHONY: collectstatic
collectstatic:
	poetry run python src/manage.py collectstatic --settings=${settings} --no-input --ignore=node_modules --ignore=*.scss --ignore=*.json --ignore=vite.config.js

.PHONY: docker-up 
docker-up:
	docker compose up -d --build

.PHONY: shell
shell:
	poetry run python src/manage.py shell

.PHONY: shell_plus
shell_plus:
	poetry run python src/manage.py shell_plus

.PHONY: dbbackup
dbbackup:
	poetry run python src/manage.py dbbackup

settings ?= core.settings.production
.PHONY: clear_cache 
clear_cache:
	poetry run python src/manage.py clear_cache --settings=${settings}

.PHONY: loaddata
loaddata:
	poetry run python src/manage.py loaddata --database=default groups clusters locations beneficiaries types currencies disaggregation donors facility_sites organizations activity_domain activity_type indicator stock_item stock_unit 