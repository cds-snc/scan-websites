.PHONY: dev
dev:
	uvicorn main:app --reload

.PHONY: fmt
fmt:
	black . $(ARGS)

.PHONY: install
install:
	pip3 install --user -r requirements.txt

.PHONY: lint
lint:
	pylint .

.PHONY: test
test:
	coverage run -m pytest -s -vv tests &&\
	coverage report -m