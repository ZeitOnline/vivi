import pytest
import requests


CONFIG_STAGING = {
    'browser': {'baseurl': 'https://www.staging.zeit.de'},
    'storage': 'http://content-storage.staging.zon.zeit.de/internal',
    'elasticsearch': 'https://tms-es.staging.zon.zeit.de/zeit_content/_search',
}


CONFIG_PRODUCTION = {
    'browser': {'baseurl': 'https://www.zeit.de'},
    'storage': 'http://content-storage.prod.zon.zeit.de/internal',
    'elasticsearch': 'https://tms-es.zon.zeit.de/zeit_content/_search',
}


@pytest.fixture(scope='session')
def nightwatch_config(nightwatch_environment):
    config = globals()['CONFIG_%s' % nightwatch_environment.upper()]
    return dict(config, environment=nightwatch_environment)


@pytest.fixture(scope='session')
def config(nightwatch_config):  # shorter spelling for our tests
    return nightwatch_config


def pytest_configure(config):
    config.option.prometheus_job_name = 'vivi-%s' % config.option.nightwatch_environment
    if config.option.prometheus_extra_labels is None:
        config.option.prometheus_extra_labels = []
    config.option.prometheus_extra_labels.append('project=vivi')


class StorageClient:
    def __init__(self, url):
        self.url = url
        self.http = requests.Session()

    def _request(self, verb, url, **kw):
        r = self.http.request(verb, self.url + '/api/v1' + url, **kw)
        r.raise_for_status()
        return r

    def set_property(self, path, ns, name, value):
        self._request('put', f'/resource{path}', json={ns: {name: value}})

    def set_body(self, path, body):
        self._request(
            'put',
            f'/resource{path}',
            data=body,
            headers={'content-type': 'application/octet-stream'},
        )

    def publish(self, path):
        self._request('post', f'/publish{path}')


@pytest.fixture(scope='session')
def vivi(config):
    return StorageClient(config['storage'])
