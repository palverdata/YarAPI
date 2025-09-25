# syntax = docker/dockerfile:1.2

FROM python:3.11

ARG POETRY_REQUESTS_TIMEOUT=1200

RUN apt-get update && \
    apt-get install -y git python3-dev

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi -vvv

COPY . /app

# Ensure /app is writable by all users
RUN chmod -R 777 /app

RUN chmod -R 777 /app/extensions

ENTRYPOINT ["poetry", "run", "python", "main.py"]
