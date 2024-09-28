SHELL = /bin/bash
SRC = src

PYTHON = python3

# Environment
venv:
	${PYTHON} -m venv tele_venv
	source tele_venv/bin/activate && \
	${PYTHON} -m pip install pip setuptools wheel && \
	${PYTHON} -m pip install --upgrade pip && \
	${PYTHON} -m pip install -e .

# Style
style:
	black .
	flake8 ${SRC}/
	${PYTHON} -m isort ${SRC}/

test:
	${PYTHON} -m flake8 ./tests ./src
	${PYTHON} -m mypy ./tests ./src
	${PYTHON} -m pytest -s --durations=0 --disable-warnings tests/