import os

import pytest
import requests

import zeit.msal
import zeit.nightwatch


CONFIG_STAGING = {
    'www': 'https://www.staging.zeit.de',
    'vivi_ui': 'https://vivi.staging.zeit.de',
    'vivi_admin': 'https://vivi.staging.zon.zeit.de',
    'admin_user': 'nightwatch',
    'admin_password': os.environ['VIVI_XMLRPC_PASSWORD'],
    'storage': 'https://content-storage.staging.zon.zeit.de',
    'tms': f'https://zeit:{os.environ["TMS_PASSWORD"]}@zeit-online-tms-stage.rtrsupport.de/api',
}


CONFIG_PRODUCTION = {
    'www': 'https://www.zeit.de',
    'vivi_ui': 'https://vivi.zeit.de',
    'vivi_admin': 'https://vivi.prod.zon.zeit.de',
    'admin_user': 'nightwatch',
    'admin_password': os.environ['VIVI_XMLRPC_PASSWORD'],
    'storage': 'https://content-storage.prod.zon.zeit.de',
    'tms': f'https://zeit:{os.environ["TMS_PASSWORD"]}@zeit-online-varnish.rtrsupport.de/api',
}


@pytest.fixture(scope='session')
def nightwatch_config(nightwatch_environment):
    config = globals()['CONFIG_%s' % nightwatch_environment.upper()]
    return dict(config, environment=nightwatch_environment)


@pytest.fixture(scope='session')
def config(nightwatch_config):  # shorter spelling for our tests
    return nightwatch_config


def pytest_configure(config):
    config.option.browser = ['firefox']


@pytest.fixture
def http(nightwatch_config, oidc_token):
    baseurl = nightwatch_config.get('www', '')
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


class StorageClient:
    def __init__(self, storage_url, vivi_url, user, password):
        self.storage_url = storage_url
        self.vivi_url = vivi_url.replace('https://', f'https://{user}:{password}@')
        self.http = requests.Session()

    def _request(self, verb, url, **kw):
        r = self.http.request(verb, self.storage_url + url, **kw)
        r.raise_for_status()
        return r

    def get_property(self, path, ns, name):
        return self._request(
            'get',
            f'/internal/api/v1/resource{path}',
            params={'ns': ns, 'name': name},
            headers={'accept': 'text/plain'},
        ).text

    def set_property(self, path, ns, name, value):
        self._request('put', f'/internal/api/v1/resource{path}', json={ns: {name: value}})

    def set_body(self, path, body):
        self._request(
            'put',
            f'/internal/api/v1/resource{path}',
            data=body,
            headers={'content-type': 'application/octet-stream'},
        )

    def get_uuid(self, path):
        return self._request(
            'get',
            f'/internal/api/v1/resource{path}',
            headers={'accept': 'text/plain'},
            params={'ns': 'document', 'name': 'uuid'},
        ).text.strip()

    def publish(self, path):
        return self._request('post', f'/internal/api/v1/publish{path}').json()['job-id']

    def retract(self, path):
        return self._request('post', f'/internal/api/v1/retract{path}').json()['job-id']

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
    return StorageClient(
        config['storage'], config['vivi_admin'], config['admin_user'], config['admin_password']
    )


@pytest.fixture
def tms(config):
    return zeit.nightwatch.Browser(config['tms'])


@pytest.fixture(scope='session')
def azure_id_token():
    path = f'{os.getcwd()}/msal.json'
    cache = f'file://{path}'
    auth = zeit.msal.Authenticator(
        os.environ.get('AD_CLIENT_ID'), os.environ.get('AD_CLIENT_SECRET'), cache
    )
    # Change into smoketest directory and run:
    # uv run msal-token --client-id=myclient --client-secret=mysecret \
    #       --cache-url=file:///tmp/msal.json login
    # Secrets are stored in zon/v1/azure/activedirectory/oidc/<staging/production>/vivi
    # Replace new refresh token in secret with key refresh_token
    if not os.path.exists(path):
        auth.login_with_refresh_token(os.environ.get('AD_REFRESH_TOKEN'))
    return auth.get_id_token()
