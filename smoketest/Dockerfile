# See https://github.com/ZeitOnline/gh-action-workflows/blob/main/.github/workflows/nightwatch-build.yaml
FROM python:3.13.2-slim@sha256:6b3223eb4d93718828223966ad316909c39813dee3ee9395204940500792b740 as nightwatch
WORKDIR /app
RUN pip --no-cache-dir install pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv sync
RUN pipenv run playwright install firefox --with-deps
COPY *.py ./
# See https://github.com/ZeitOnline/kustomize/blob/main/components/nightwatch/deployment.yaml
ENTRYPOINT ["pipenv", "run", "pytest", "--tb=native"]
