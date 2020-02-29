# poetry run pytest -v
path='otlk'
poetry run isort -rc ${path}
poetry run black ${path}
poetry run flake8  ${path}

