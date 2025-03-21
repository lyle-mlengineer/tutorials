install-dev:
	@pip install -r requirements-dev.txt

install:
	@pip install -r requirements.txt

pre-commit:
	@pre-commit install

initial-tag:
	@git tag -a -m "Initial tag." v0.0.1

init-cz:
	@cz init

bump-tag:
	@cz bump --check-consistency --changelog

# build|ci|docs|feat|fix|perf|refactor|style|test|chore|revert|bump

lint:
	@black .
	@isort .
	@flake8 .