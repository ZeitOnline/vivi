# See https://github.com/ZeitOnline/gh-action-workflows/blob/main/.github/workflows/nightwatch-build.yaml
FROM python:3.13.5-slim@sha256:6544e0e002b40ae0f59bc3618b07c1e48064c4faed3a15ae2fbd2e8f663e8283 as nightwatch

COPY --from=ghcr.io/astral-sh/uv:0.7.21@sha256:a64333b61f96312df88eafce95121b017cbff72033ab2dbc6398edb4f24a75dd /uv /usr/bin/
ENV UV_NO_MANAGED_PYTHON=1 \
    UV_NO_CACHE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_FROZEN=1

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync
RUN uv run playwright install firefox --with-deps
COPY *.py ./

# Duplicated from ZeitOnline/kustomize:nightwatch/deployment.yaml for local `bin/test`
ENTRYPOINT ["uv", "run", "pytest", "--tb=native"]
