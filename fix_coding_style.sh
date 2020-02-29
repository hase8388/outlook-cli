# poetry run pytest -v
path='oltk'
poetry run isort -rc ${path}
poetry run black ${path}
poetry run flake8  ${path}

