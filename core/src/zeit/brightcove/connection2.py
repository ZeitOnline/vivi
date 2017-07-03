import logging
import requests
import zeit.brightcove.interfaces
import zope.app.appsetup.product
import zope.interface


log = logging.getLogger(__name__)


class CMSAPI(object):
    """Connection to the Brightcove "CMS API".

    * Overview: <https://support.brightcove.com/overview-cms-api>
    * API Reference: <https://brightcovelearning.github.io
        /Brightcove-API-References/cms-api/v1/doc/index.html>
    """

    zope.interface.implements(zeit.brightcove.interfaces.ICMSAPI)

    MAX_RETRIES = 2
    _access_token = None

    def __init__(self, base_url, oauth_url, client_id, client_secret, timeout):
        self.base_url = base_url
        self.oauth_url = oauth_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.timeout = timeout

    def get_video(self, id):
        return self._request('GET /videos/%s' % id)

    def get_video_sources(self, id):
        return self._request('GET /videos/%s/sources' % id)

    def update_video(self, bcvideo):
        self._request('PATCH /videos/%s' % bcvideo.id, body=bcvideo.write_data)

    def _request(self, request, body=None, _retries=0):
        if _retries >= self.MAX_RETRIES:
            raise RuntimeError('Maximum retries exceeded for %s' % request)

        verb, path = request.split(' ')
        log.info('%s%s', request, ' (retry)' if _retries else '')

        try:
            response = requests.request(
                verb.lower(), self.base_url + path, json=body,
                headers={'Authorization': 'Bearer %s' % self._access_token},
                timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.RequestException, err:
            status = getattr(err.response, 'status_code', 510)
            if status == 401:
                log.debug('Refreshing access token')
                # We're not taking any precautions about several threads
                # hitting an expired token simultaneously. Preventing duplicate
                # "get token" requests would require a lot of effort (e.g.
                # dogpile lock), which doesn't seem worthwile. Instead we don't
                # bother at all, since a normal lock would only accomplish
                # serializing those requests, which isn't much of a plus.
                self._access_token = self._retrieve_access_token()
                return self._request(request, body=body, _retries=_retries + 1)
            message = getattr(err.response, 'text', '<no message>')
            err.args = (u'%s: %s' % (err.args[0], message),) + err.args[1:]
            log.error('%s returned %s', request, status, exc_info=True)
            raise

        try:
            return response.json()
        except:
            log.error('%s returned invalid json %r', request, response.text)
            raise ValueError('No valid JSON found for %s' % request)

    def _retrieve_access_token(self):
        # See <http://docs.brightcove.com/en/video-cloud/oauth-api
        #      /getting-started/oauth-api-overview.html>
        response = requests.post(
            self.oauth_url + '/access_token',
            data={'grant_type': 'client_credentials'},
            auth=(self.client_id, self.client_secret),
            timeout=self.timeout)
        response.raise_for_status()
        return response.json()['access_token']


def from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.brightcove')
    return CMSAPI(
        config['api-url'],
        config['oauth-url'],
        config['client-id'],
        config['client-secret'],
        float(config['timeout'])
    )
