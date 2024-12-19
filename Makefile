.PHONY: help
help:
	@echo "Available commands:"
	@grep -E '^\.\PHONY: ' $(MAKEFILE_LIST) | sed 's/\.PHONY: //; s/^/  /'

.PHONY: install
install:
	poetry install

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
	cd src/static && npm run dev

.PHONY: ruff-watch
ruff-watch:
	ruff check ./src --watch

.PHONY: dev
dev:
	make -j3 serve vite

.PHONY: vite-host
vite-host:
	cd src/static && npm run dev -- --host

.PHONY: npm-install
npm-install:
	cd src/static && npm install

.PHONY: npm-build
npm-build:
	cd src/static && npm run build

.PHONY: npm-update
npm-update:
	npm-install npm-build;

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

.PHONY: seed
seed:
	cd scripts && python migrate_mongodb.py
	poetry run python src/manage.py load_activities

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

.PHONY: run-dependencies
run-dependencies:
	docker-compose -f docker-compose.dev.yml up -d --build

.PHONY: shell
shell:
	poetry run python src/manage.py shell

.PHONY: shell_plus
shell_plus:
	poetry run python src/manage.py shell_plus

.PHONY: dbbackup
dbbackup:
	poetry run python src/manage.py dbbackup

.PHONY: clear_cache 
clear_cache:
	poetry run python src/manage.py clear_cache

.PHONY: loaddata
loaddata:
	poetry run python src/manage.py loaddata --database=default groups clusters locations beneficiaries types currencies disaggregation donors facility_sites organizations activity_domain activity_type indicator stock_item stock_unit 