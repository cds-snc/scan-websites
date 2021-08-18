.PHONY: dev fmt install lint migrations test fmt-ci

build:

dev:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

fmt:
	black . $(ARGS)

install:
	pip3 install --user -r requirements.txt

install-dev:
	pip3 install --user -r requirements_dev.txt

lint:
	flake8 .

migrations:
	cd db_migrations &&\
	alembic upgrade head

test:
	coverage run -m pytest -s -vv tests &&\
	coverage report -m

fmt-ci:
	black --check .