Runs on Python 3.14. Dependencies are managed with Pipenv:

	pipenv install

## Running the project:

### Start the backend:

	gunicorn backend.gunicorn:application

### Run tests:

	python test.py

Tests hit the live OMDB API, so they need network access.

### Lint:

	flake8
