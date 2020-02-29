# poetry run pytest -v
path='tendra_cli'
poetry run isort -rc ${path}
poetry run black ${path}
poetry run flake8  ${path}

