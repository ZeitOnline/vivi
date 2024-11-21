# See https://github.com/ZeitOnline/gh-action-workflows/blob/main/.github/workflows/nightwatch-build.yaml
FROM python:3.13.0-slim@sha256:4efa69bf17cfbd83a9942e60e2642335c3b397448e00410063a0421f9727c4c4 as nightwatch
WORKDIR /app
RUN pip --no-cache-dir install pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv sync
COPY *.py ./
# See https://github.com/ZeitOnline/kustomize/blob/main/components/nightwatch/deployment.yaml
ENTRYPOINT ["pipenv", "run", "pytest", "--tb=native"]
