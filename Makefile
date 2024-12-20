
install:
	poetry install

lint:
	poetry run ruff check page_analyzer/

dev:
	poetry run flask --app page_analyzer:app run

build:
	./build.sh

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app
