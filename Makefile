
export FLASK_APP=feedon
export FLASK_RUN_PORT=3000
export FLASK_RUN_HOST=0.0.0.0
export DB_PATH=$(CWD)/.data/feedon-dev.db

.PHONY: dev

dev:
	poetry run flask --app feedon run -h 0.0.0.0 --debug -p 8000
