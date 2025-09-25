# syntax = docker/dockerfile:1.2

FROM python:3.11

ARG POETRY_REQUESTS_TIMEOUT=1200

RUN apt-get update && \
    apt-get install -y git python3-dev openssh-client && \
    mkdir -p /root/.ssh && \
    ssh-keyscan github.com >> /root/.ssh/known_hosts

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

ENV GIT_SSH_COMMAND "ssh -v"

RUN --mount=type=secret,id=id_rsa,dst=/root/.ssh/id_rsa \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi -vvv

COPY . /app

# Ensure /app is writable by all users
RUN chmod -R 777 /app

RUN chmod -R 777 /app/extensions

ENTRYPOINT ["poetry", "run", "python", "main.py"]
