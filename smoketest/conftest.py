import os

import pytest
import requests


XMLRPC_AUTH = 'nightwatch:' + os.environ['VIVI_XMLRPC_PASSWORD']
CONFIG_STAGING = {
    'browser': {'baseurl': 'https://www.staging.zeit.de'},
    'storage': 'https://content-storage.staging.zon.zeit.de/internal',
    'vivi': f'https://{XMLRPC_AUTH}@vivi.staging.zon.zeit.de',
    'elasticsearch': 'https://tms-es.staging.zon.zeit.de/zeit_content/_search',
}


CONFIG_PRODUCTION = {
    'browser': {'baseurl': 'https://www.zeit.de'},
    'storage': 'https://content-storage.prod.zon.zeit.de/internal',
    'vivi': f'https://{XMLRPC_AUTH}@vivi.prod.zon.zeit.de',
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
    def __init__(self, storage_url, vivi_url):
        self.storage_url = storage_url
        self.vivi_url = vivi_url
        self.http = requests.Session()

    def _request(self, verb, url, **kw):
        r = self.http.request(verb, self.storage_url + '/api/v1' + url, **kw)
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
        return self._request('post', f'/publish{path}').json()['job-id']

    def job_status(self, job):
        r = self.http.get(self.vivi_url + '/@@job-status', params={'job': job})
        r.raise_for_status()
        return r.json()

    def job_result(self, job):
        r = self.http.get(self.vivi_url + '/@@job-result', params={'job': job})
        r.raise_for_status()
        return r.text


@pytest.fixture(scope='session')
def vivi(config):
    return StorageClient(config['storage'], config['vivi'])
