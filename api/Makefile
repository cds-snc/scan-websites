.PHONY: dev
dev:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

.PHONY: fmt
fmt:
	black . $(ARGS)

.PHONY: install
install:
	pip3 install --user -r requirements.txt

.PHONY: lint
lint:
	flake8 .

.PHONY: migrations
migrations:
	cd db_migrations &&\
	alembic upgrade head

.PHONY: test
test:
	coverage run -m pytest -s -vv tests &&\
	coverage report -m