VENV=.venv/bin/python3
PIP=.venv/bin/python3 -m pip
MANAGE=$(VENV) manage.py

all: help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

migrate: ## Apply migrations to the database
#	@$(MANAGE) migrate allauth.socialaccount
#	@$(MANAGE) migrate allauth.socialaccount.providers.github
	@$(MANAGE) migrate

makemigrations: ## Create new migrations based on the changes to the models
	@$(MANAGE) makemigrations

test: ## Run all tests
	@$(VENV) -m pytest .

cov: ## Run all tests and create coverage
	@$(VENV) -m pytest --cov .
	@$(VENV) -m coverage xml
	@$(VENV) -m coverage html

fmt: ## Format all files
	@$(VENV) -m black .

lint: ## Check if all files have been formated
	@$(VENV) -m black --check .

celery-worker: ## Run a celery worker
	@$(VENV) -m celery -A tsg worker -l debug

celery-beat: ## Run the celery beat
	@$(VENV) -m celery -A tsg beat -l debug

runserver: ## Run the dev server
	@$(MANAGE) runserver

deps: ## Install all dependencies
	@make set_virtualenv
	@$(PIP) install setuptools --upgrade
	@$(PIP) install wheel
	@$(PIP) install -r requirements.txt

check: ## Run all django checks
	@$(MANAGE) check

freeze: ## Update the requirements.txt
	@mv requirements.txt requirements_old.txt
	@$(PIP) freeze > requirements.txt


set_virtualenv:
ifeq ($(wildcard ./.venv/.*),)
	@echo "Did not find ~/.venv"
	@echo "Now installing virtual env!"
	python3 -m venv .venv
	make deps
endif
