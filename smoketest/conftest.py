import os

import pytest
import requests

import zeit.msal
import zeit.nightwatch


XMLRPC_AUTH = 'nightwatch:' + os.environ['VIVI_XMLRPC_PASSWORD']
CONFIG_STAGING = {
    'www_baseurl': 'https://www.staging.zeit.de',
    'vivi_baseurl': 'https://vivi.staging.zeit.de',
    'storage': 'https://content-storage.staging.zon.zeit.de/internal',
    'vivi': f'https://{XMLRPC_AUTH}@vivi.staging.zon.zeit.de',
    'elasticsearch': 'https://tms-es.staging.zon.zeit.de/zeit_content/_search',
}


CONFIG_PRODUCTION = {
    'www_baseurl': 'https://www.zeit.de',
    'vivi_baseurl': 'https://vivi.zeit.de',
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


@pytest.fixture
def http(nightwatch_config, oidc_token):
    baseurl = nightwatch_config.get('www_baseurl', '')
    browser = zeit.nightwatch.Browser(baseurl=baseurl)
    if oidc_token:
        browser.session.cookies.set('zeit_oidc_www_staging', oidc_token)
    return browser


@pytest.fixture(scope='session')
def oidc_token(nightwatch_config):
    if nightwatch_config['environment'] != 'staging':
        return None
    with requests.Session() as http:
        r = http.post(
            'https://openid.zeit.de/realms/zeit-online/protocol/openid-connect/token',
            data={'grant_type': 'client_credentials', 'scope': 'openid'},
            auth=(os.environ['OIDC_CLIENT_ID'], os.environ['OIDC_CLIENT_SECRET']),
        )
        r.raise_for_status()
        return r.json()['id_token']


@pytest.fixture(scope='session')
def firefox_page(playwright, azure_id_token, nightwatch_config):
    firefox = playwright.firefox
    browser = firefox.launch()
    context = browser.new_context(
        base_url=nightwatch_config['vivi_baseurl'],
        extra_http_headers={'Authorization': f'Bearer {azure_id_token}'},
    )
    page = context.new_page()
    yield page
    context.close()
    browser.close()


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


@pytest.fixture(scope='session')
def azure_id_token():
    path = f'{os.getcwd()}/msal.json'
    cache = f'file://{path}'
    auth = zeit.msal.Authenticator(
        os.environ.get('AD_CLIENT_ID'), os.environ.get('AD_CLIENT_SECRET'), cache
    )
    # Change into smoketest directory and run:
    # >> pipenv run msal-token --client-id=myclient --client-secret=mysecret \ # noqa: E800
    #       --cache-url=file:///tmp/msal.json login
    # Secrets are stored in zon/v1/azure/activedirectory/oidc/<staging/production>/vivi
    # Replace new refresh token in secret with key refresh_token
    if not os.path.exists(path):
        auth.login_with_refresh_token(os.environ.get('AD_REFRESH_TOKEN'))
    return auth.get_id_token()
