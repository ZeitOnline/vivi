# ZeitOnline/gh-action-workflows:nightwatch-build.yaml uses `target: nightwatch`
FROM python:3.14.1-slim@sha256:9200f77df642830fcded51b873dde4d8f0643b46713823ee0c104df955107ee3 AS nightwatch

COPY --from=ghcr.io/astral-sh/uv:0.9.15@sha256:4c1ad814fe658851f50ff95ecd6948673fffddb0d7994bdb019dcb58227abd52 /uv /usr/bin/
ENV UV_NO_MANAGED_PYTHON=1 \
    UV_NO_CACHE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_FROZEN=1 \
    UV_INDEX_PYPI_ZON_USERNAME="oauth2accesstoken"

WORKDIR /app
RUN groupadd --gid=10000 app && \
    useradd --uid=10000 --gid=app --no-user-group \
    --create-home --home-dir /tmp app && \
    chown -R app:app /app
USER app
ENV PATH=/app/.venv/bin:$PATH

COPY pyproject.toml uv.lock ./
RUN --mount=type=secret,id=GCLOUD_TOKEN,env=UV_INDEX_PYPI_ZON_PASSWORD \
    uv sync

ENV PLAYWRIGHT_BROWSERS_PATH=/opt/playwright
USER root
RUN playwright install --with-deps firefox
USER app

COPY *.py ./
ENTRYPOINT ["pytest", "--tb=native"]

# Security updates run last, to intentionally bust the docker cache.
USER root
RUN apt-get update && apt-get -y upgrade && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
USER app
