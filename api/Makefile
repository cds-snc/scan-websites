test_case = '' # Run all tests by default; otherwise run user specified test

.PHONY: dev fmt install lint migrations test fmt-ci lint-ci build install-dev seed

build: ;

dev:
	FASTAPI_SECRET_KEY='e8cb82f5-b966-4496-b96e-8c021892e265' uvicorn main:app --reload --host 0.0.0.0 --port 8000

fmt:
	black . $(ARGS)

install:
	pip3 install --user -r requirements.txt

install-dev:
	pip3 install --user -r requirements_dev.txt

lint:
	flake8 .

lint-ci:
	flake8 .

setup-db: migrations seed

migrations:
	cd db_migrations &&\
	alembic upgrade head

seed: 
	python database/seed.py

test:
	FASTAPI_SECRET_KEY='e8cb82f5-b966-4496-b96e-8c021892e265' CI=True coverage run -m pytest -k $(test_case) -s -vv tests &&\
	coverage report -m

fmt-ci:
	black --check .