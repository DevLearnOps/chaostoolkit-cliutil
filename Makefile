.PHONY: test fmt

install:
	pipenv install --dev
	pipenv run pip install --editable .

test:
	pipenv run pytest tests/

fmt:
	find src/chaoscli/ -type f -name '*.py' \
		| xargs pipenv run isort
	find src/chaoscli/ -type f -name '*.py' \
		| xargs pipenv run black
