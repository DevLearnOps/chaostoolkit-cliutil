.PHONY: test fmt

test:
	pipenv run pytest tests/

fmt:
	find src/chaoscli/ -type f -name '*.py' \
		| xargs pipenv run isort
	find src/chaoscli/ -type f -name '*.py' \
		| xargs pipenv run black
