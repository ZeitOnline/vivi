import logging
import urllib.parse

from zope.cachedescriptors.property import Lazy as cachedproperty
import msal
import persistent
import requests
import requests.exceptions
import zope.interface

import zeit.cms.config


log = logging.getLogger(__name__)


class IActiveDirectory(zope.interface.Interface):
    pass


class ITokenCache(zope.interface.Interface):
    pass


@zope.interface.implementer(IActiveDirectory)
class AzureAD:
    graph_url = 'https://graph.microsoft.com/v1.0'

    def __init__(self, tenant_id, client_id, client_secret, timeout=None):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.timeout = timeout

    @cachedproperty
    def app(self):
        app = msal.ConfidentialClientApplication(
            self.client_id,
            self.client_secret,
            authority='https://login.microsoftonline.com/%s' % self.tenant_id,
        )
        app.token_cache = zope.component.getUtility(ITokenCache)
        app.http_client.close()
        return app

    def _request(self, request, **kw):
        kw.setdefault('timeout', self.timeout)
        with requests.Session() as http:
            http.headers['Authorization'] = 'Bearer %s' % self._auth_token()
            method, path = request.split(' ')
            r = getattr(http, method.lower())(self.graph_url + path, **kw)
        if not r.ok:
            r.reason = '%s: %s' % (r.reason, r.text)
        r.raise_for_status()
        return r.json()

    _graph_api_scopes = ['https://graph.microsoft.com/.default']

    def _auth_token(self):
        # MSAL unfortunately has no info logging, e.g. for "calling refresh"
        token = self.app.acquire_token_silent(self._graph_api_scopes, account=None)
        if not token:
            log.info('Retrieving access token with client_secret')
            token = self.app.acquire_token_for_client(self._graph_api_scopes)
            self.app.http_client.close()
        if 'error' in token:
            raise RuntimeError(str(token))
        return token['access_token']

    def get_user(self, upn):
        """Look up user by userPrincipalName, for which ZEIT AD uses the
        (pseudo-) email address. Returns a dict with keys `displayName` and
        `userPrincipalName`.
        """
        try:
            return self._request(
                'GET /users/%s' % urllib.parse.quote(upn),
                params={'$select': 'displayName,userPrincipalName'},
            )
        except requests.exceptions.RequestException as e:
            if getattr(e.response, 'status_code', 599) != 404:
                log.warning('AD get_user(%r) failed', upn, exc_info=True)
            return None

    def search_users(self, query):
        """Search for users by substring of their displayName.
        Returns a list of dicts with keys `displayName` and `userPrincipalName`
        """
        try:
            data = self._request(
                'GET /users',
                headers={'ConsistencyLevel': 'eventual'},
                params={
                    '$select': 'displayName,userPrincipalName',
                    '$search': '"displayName:%s"' % query,
                },
            )
            return data.get('value', [])
        except requests.exceptions.RequestException:
            log.warning('AD search_users(%r) failed', query, exc_info=True)
            return []


@zope.interface.implementer(IActiveDirectory)
def from_product_config():
    config = zeit.cms.config.package('zeit.authentication')
    return AzureAD(
        config['ad-tenant'],
        config['ad-client-id'],
        config['ad-client-secret'],
        float(config['ad-timeout']),
    )


@zope.interface.implementer(ITokenCache)
class PersistentTokenCache(msal.TokenCache, persistent.Persistent):
    """ZODB-based storage for the access- and refresh token."""

    def add(self, *args, **kw):
        super().add(*args, **kw)
        self._p_changed = True

    def modify(self, *args, **kw):
        super().modify(*args, **kw)
        self._p_changed = True

    def __getstate__(self):
        """MSAL sets up a lot of static stuff in init instead of on the class,
        so we restrict the data to pickle to what's actually relevant."""
        return {'_cache': self._cache}

    def __setstate__(self, state):
        self.__init__()
        self.__dict__.update(state)

    def _p_resolveConflict(self, old, commited, newstate):
        """Many places are looking up principals; so to prevent this object
        from being a ConflictError hotspot e.g. when the token expires, we use
        a 'last one wins' strategy instead of forcing a retry -- since we don't
        care which exact access token we store, as long as it's a valid one."""
        return newstate
