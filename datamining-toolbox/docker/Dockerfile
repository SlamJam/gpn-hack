#syntax=docker/dockerfile:1.2


FROM python:3.9-slim as final-base
# ENV PYTHONFAULTHANDLER=1 \
#     PYTHONHASHSEED=random \
#     PYTHONUNBUFFERED=1 \
#     PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

FROM python:3.9 as builder-base
WORKDIR /app


# ------------------------------------------------------------------------------------------------------------------- #

FROM builder-base as builder
ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# Install deps & tools
RUN apt-get update && apt-get install -y build-essential cmake
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -
# RUN test -d /root/.local/bin
RUN python -m venv /venv --upgrade-deps

# poetry's bin
ENV PATH=/root/.local/bin:$PATH

# Install requirements into venv
COPY pyproject.toml poetry.lock ./
RUN [ "/bin/bash", "-c", "set -o pipefail && poetry export --format requirements.txt \
    | /venv/bin/pip install -r /dev/stdin --require-hashes --no-deps" ]

# Build & install our project into venv
COPY . .
RUN poetry build --format wheel && /venv/bin/pip install --no-index --no-deps dist/*.whl

# ------------------------------------------------------------------------------------------------------------------- #

FROM final-base
# RUN apt-get update && apt-get install -y
RUN mkdir -p /var/lib/luigi-server/
COPY docker/docker-entrypoint.sh /

COPY --from=builder /venv /venv
ENV PATH=/venv/bin:$PATH

ENTRYPOINT [ "/docker-entrypoint.sh" ]
CMD [ "lu", "MainTask" ]
