# See https://github.com/ZeitOnline/gh-action-workflows/blob/main/.github/workflows/nightwatch-build.yaml
FROM python:3.13.1-slim@sha256:f41a75c9cee9391c09e0139f7b49d4b1fbb119944ec740ecce4040626dc07bed as nightwatch
WORKDIR /app
RUN pip --no-cache-dir install pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv sync
COPY *.py ./
# See https://github.com/ZeitOnline/kustomize/blob/main/components/nightwatch/deployment.yaml
ENTRYPOINT ["pipenv", "run", "pytest", "--tb=native"]
