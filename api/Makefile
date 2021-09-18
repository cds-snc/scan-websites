.PHONY: dev fmt install lint migrations test fmt-ci lint-ci build install-dev

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

migrations:
	cd db_migrations &&\
	alembic upgrade head

test:
	FASTAPI_SECRET_KEY='e8cb82f5-b966-4496-b96e-8c021892e265' CI=True coverage run -m pytest -s -vv tests &&\
	coverage report -m

fmt-ci:
	black --check .