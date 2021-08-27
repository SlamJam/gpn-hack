FROM python:3.9-slim

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends apt-utils && \
    apt-get install -y --no-install-recommends build-essential cmake git && \
    apt-get install -y --no-install-recommends curl ca-certificates gnupg
RUN curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN echo "deb http://apt.postgresql.org/pub/repos/apt buster-pgdg main" > /etc/apt/sources.list.d/pgdg.list

# For psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev libopenblas-dev liblapack-dev

# For developer comfort
RUN apt-get update && apt-get install -y --no-install-recommends fish && \
    usermod root --shell /usr/bin/fish

RUN pip install --no-cache-dir -U pip setuptools wheel poetry

WORKDIR /workspace
# COPY pyproject.toml poetry.lock ./

# RUN poetry install

ENTRYPOINT [ "/usr/bin/fish" ]
