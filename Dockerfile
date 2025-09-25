# syntax = docker/dockerfile:1.2

FROM python:3.11

ARG POETRY_REQUESTS_TIMEOUT=1200

RUN apt-get update && \
    apt-get install -y git python3-dev openssh-client && \
    mkdir -p /root/.ssh && \
    ssh-keyscan github.com >> /root/.ssh/known_hosts

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

# add this (works on Poetry >=1.2; new name in 2.x)
ENV POETRY_SYSTEM_GIT_CLIENT=true
# (for older 1.x just in case)
ENV POETRY_EXPERIMENTAL_SYSTEM_GIT_CLIENT=true

# optional: be explicit about the identity and avoid noisy -v
ENV GIT_SSH_COMMAND="ssh -i /root/.ssh/id_rsa -o StrictHostKeyChecking=yes"

# ensure Poetry also has the config persisted (belt & suspenders)
RUN --mount=type=secret,id=id_rsa,dst=/root/.ssh/id_rsa \
    pip install poetry && \
    poetry config system-git-client true && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi -vvv

COPY . /app

# Ensure /app is writable by all users
RUN chmod -R 777 /app

ENTRYPOINT ["poetry", "run", "python", "main.py"]
