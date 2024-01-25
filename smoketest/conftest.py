from io import BytesIO
from urllib.parse import urlparse
import os
import xmlrpc.client

import pytest
import webdav3.client


XMLRPC_AUTH = 'nightwatch:' + os.environ['VIVI_XMLRPC_PASSWORD']
CONFIG_STAGING = {
    'browser': {'baseurl': 'https://www.staging.zeit.de'},
    'vivi': {
        'dav_url': 'http://cms-backend.staging.zeit.de:9000',
        'xmlrpc_url': f'https://{XMLRPC_AUTH}@vivi-frontend.staging.zeit.de:9090/',
    },
    'elasticsearch': 'https://tms-es.staging.zon.zeit.de/zeit_content/_search',
}


CONFIG_PRODUCTION = {
    'browser': {'baseurl': 'https://www.zeit.de'},
    'vivi': {
        'dav_url': 'http://cms-backend.zeit.de:9000',
        'xmlrpc_url': f'https://{XMLRPC_AUTH}@vivi-frontend.zeit.de:9090/',
    },
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


class ViviClient:
    def __init__(self, dav_url, xmlrpc_url):
        self.dav = webdav3.client.Client({'webdav_hostname': dav_url})
        self.xmlrpc = xmlrpc.client.ServerProxy(xmlrpc_url)

    def set_property(self, unique_id, ns, name, value):
        path = '/cms/work' + urlparse(unique_id).path
        if not ns.startswith('http'):
            ns = 'http://namespaces.zeit.de/CMS/%s' % ns
        self.dav.set_property(path, {'namespace': ns, 'name': name, 'value': value})

    def put(self, unique_id, body):
        path = '/cms/work' + urlparse(unique_id).path
        self.dav.upload_to(BytesIO(body.encode('utf-8')), path)

    def refresh_dav_cache(self, unique_id):
        if unique_id.startswith('/'):
            unique_id = 'http://xml.zeit.de' + unique_id
        self.xmlrpc.invalidate(unique_id)

    def publish(self, unique_id):
        if unique_id.startswith('/'):
            unique_id = 'http://xml.zeit.de' + unique_id
        self.xmlrpc.publish(unique_id)


@pytest.fixture(scope='session')
def vivi(config):
    return ViviClient(**config['vivi'])
