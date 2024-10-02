import logging

import requests
import zope.interface

import zeit.brightcove.interfaces
import zeit.cms.config
import zeit.content.video.interfaces


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.brightcove.interfaces.ICMSAPI)
class CMSAPI:
    """Connection to the Brightcove "CMS API".

    * Overview: <https://support.brightcove.com/overview-cms-api>
    * API Reference: <https://brightcovelearning.github.io
        /Brightcove-API-References/cms-api/v1/doc/index.html>
    """

    MAX_RETRIES = 2
    _access_token = None

    def __init__(self, base_url, oauth_url, client_id, client_secret, timeout):
        self.base_url = base_url
        self.oauth_url = oauth_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.timeout = timeout

    def get_video(self, id):
        try:
            return self._request('GET /videos/%s' % id)
        except requests.exceptions.RequestException as err:
            status = getattr(err.response, 'status_code', None)
            if status == 404:
                return None
            raise

    def get_video_sources(self, id):
        return self._request('GET /videos/%s/sources' % id)

    def update_video(self, bcvideo):
        self._request('PATCH /videos/%s' % bcvideo.id, body=bcvideo.write_data)

    def find_videos(self, query, sort='created_at'):
        offset = 0
        retrieved = {}
        while True:
            batch = self._request(
                'GET /videos',
                params={
                    'q': query,
                    'sort': sort,
                    'offset': offset,
                    'limit': 20,
                },
            )
            # Dear Brightcove, why don't you return total_hits?
            if not batch:
                break
            offset += len(batch)
            for data in batch:
                retrieved[data['id']] = data
        return retrieved.values()

    # Helper functions to register our notification webhook,
    # see <https://support.brightcove.com/cms-api-notifications>
    def get_subscriptions(self):
        return self._request('GET /subscriptions')

    def create_subscription(self, url):
        return self._request('POST /subscriptions', {'endpoint': url, 'events': ['video-change']})

    def delete_subscription(self, id):
        self._request('DELETE /subscriptions/' + id)

    def _request(self, request, body=None, params=None, _retries=0):
        if _retries >= self.MAX_RETRIES:
            raise RuntimeError('Maximum retries exceeded for %s' % request)

        verb, path = request.split(' ')
        log.info('%s%s', request, ' (retry)' if _retries else '')

        try:
            response = requests.request(
                verb.lower(),
                self.base_url + path,
                json=body,
                params=params,
                headers={'Authorization': 'Bearer %s' % self._access_token},
                timeout=self.timeout,
            )
            log.debug(dump_request(response))
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
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
                # XXX We can't really use **kw here without making our
                # signature really vague, but that means we have to explicitly
                # pass each of our parameters.
                return self._request(request, body=body, params=params, _retries=_retries + 1)
            message = getattr(err.response, 'text', '<no message>')
            err.args = ('%s: %s' % (err.args[0], message),) + err.args[1:]
            log.error('%s returned %s', request, status, exc_info=True)
            raise

        try:
            return response.json()
        except Exception:
            log.error('%s returned invalid json %r', request, response.text)
            raise ValueError('No valid JSON found for %s' % request)

    def _retrieve_access_token(self):
        # See <http://docs.brightcove.com/en/video-cloud/oauth-api
        #      /getting-started/oauth-api-overview.html>
        response = requests.post(
            self.oauth_url + '/access_token',
            data={'grant_type': 'client_credentials'},
            auth=(self.client_id, self.client_secret),
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()['access_token']


def cms_from_product_config():
    config = zeit.cms.config.package('zeit.brightcove')
    return CMSAPI(
        config['api-url'],
        config['oauth-url'],
        config['client-id'],
        config['client-secret'],
        float(config['timeout']),
    )


@zope.interface.implementer(zeit.content.video.interfaces.IPlayer)
class PlaybackAPI:
    """Connection to the Brightcove "Playback API".

    * Overview: <https://support.brightcove.com/overview-playback-api>
    * API Reference: <https://brightcovelearning.github.io
        /Brightcove-API-References/playback-api/v1/doc/index.html>
    """

    def __init__(self, base_url, policy_key, timeout):
        self.base_url = base_url
        self.policy_key = policy_key
        self.timeout = timeout

    def get_video(self, id):
        data = {'renditions': (), 'video_still': None}
        try:
            data.update(self._request('GET /videos/%s' % id))
        except requests.exceptions.RequestException as e:
            """Error-Code: VIDEO_NOT_PLAYABLE

            The policy key provided does not permit this account or video,
            or the requested resource is inactive.
            VIDEO_NOT_PLAYABLE can be returned by single video requests.
            It indicates that the video does not pass the playable check
            (ingested, active, in schedule).
            * API-Error-Reference: <https://apis.support.brightcove.com
                /playback/references/playback-api-error-reference.html>
            """
            r = e.response
            headers = getattr(r, 'headers', {})
            if headers.get('Bcov-Error-Code') != 'VIDEO_NOT_PLAYABLE':
                log.warning(
                    'Error while retrieving video %s: %s',
                    id,
                    getattr(r, 'text', '<no message>'),
                    exc_info=True,
                )
            return data

        data['video_still'] = data.get('poster')
        data['renditions'] = []
        for item in data.get('sources', ()):
            vr = zeit.content.video.video.VideoRendition()
            vr.url = item.get('src')
            if not vr.url:
                continue
            vr.frame_width = item.get('width')
            if not vr.frame_width:
                continue
            vr.video_duration = item.get('duration')
            data['renditions'].append(vr)
        return data

    def _request(self, request, body=None, params=None, _retries=0):
        verb, path = request.split(' ')
        log.info(request)
        response = requests.request(
            verb.lower(),
            self.base_url + path,
            json=body,
            params=params,
            headers={'Authorization': 'BCOV-Policy %s' % self.policy_key},
            timeout=self.timeout,
        )
        log.debug(dump_request(response))
        response.raise_for_status()
        data = response.json()
        if not data.get('poster'):
            log.warning('No poster found for %s: %s', path, dump_request(response))
        return data


def playback_from_product_config():
    config = zeit.cms.config.package('zeit.brightcove')
    return PlaybackAPI(
        config['playback-url'], config['playback-policy-key'], float(config['playback-timeout'])
    )


def dump_request(response):
    """Debug helper. Pass a `requests` response and receive an executable curl
    command line.
    """
    request = response.request
    command = "curl -X {method} -H {headers} -d '{data}' '{uri}'"
    method = request.method
    uri = request.url
    data = request.body
    headers = ["'{0}: {1}'".format(k, v) for k, v in request.headers.items()]
    headers = ' -H '.join(headers)
    return command.format(method=method, headers=headers, data=data, uri=uri)
