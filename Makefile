.PHONY: default venv lint pretty dev-start dev-build

default:
	@echo "There is no default target."

venv:
	rm -rf venv
	python -m venv venv
	./venv/bin/pip install -r requirements.txt

lint:
	./venv/bin/black --check -l 79 backend
	./venv/bin/flake8 backend
	./venv/bin/isort -c --src backend --profile black -l 79 backend

pretty:
	./venv/bin/black -l 79 backend
	./venv/bin/flake8 backend
	./venv/bin/isort --src backend --profile black -l 79 backend

lint-win:
	./venv/Scripts/black --check -l 79 backend
	./venv/Scripts/flake8 backend
	./venv/Scripts/isort -c --src backend --profile black -l 79 backend

pretty-win:
	./venv/Scripts/black -l 79 backend
	./venv/Scripts/flake8 backend
	./venv/Scripts/isort --src backend --profile black -l 79 backend

dev-build:
	docker-compose -f deployments/docker-compose.dev.yml build --no-cache

dev-start:
	docker-compose -f deployments/docker-compose.dev.yml up --force-recreate --remove-orphans
