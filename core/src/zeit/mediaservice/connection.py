import opentelemetry.trace
import pendulum
import requests
import zope.interface

import zeit.mediaservice.interfaces


class Connection:
    def __init__(self, feed_url):
        self.feed_url = feed_url

    def get_audio_infos(self, year, volume):
        result = {}
        keycloak = zope.component.getUtility(zeit.mediaservice.interfaces.IKeycloak)
        auth_header = keycloak.authenticate()
        if not auth_header:
            return result
        response = requests.get(
            self.feed_url,
            params={'year': year, 'number': volume},
            headers=auth_header,
            timeout=2,
        )
        data = response.json()
        volumes = data.get('dataFeedElement', None)
        if not volumes:
            return result
        for part_of_volume in volumes[0]['item'].get('hasPart', []):
            for article in part_of_volume.get('hasPart', []):
                mediasync_id = article.get('identifier', None)
                mp3_object = next(
                    filter(
                        lambda x: x.get('encodingFormat') == 'audio/mpeg',
                        article.get('associatedMedia', []),
                    ),
                    None,
                )
                if mediasync_id and mp3_object:
                    if 'url' not in mp3_object:
                        err = ValueError(f'Premium audio info without URL for {mediasync_id}')
                        current_span = opentelemetry.trace.get_current_span()
                        current_span.record_exception(err)
                        continue

                    audio_duration = mp3_object.get('duration')
                    if not audio_duration:
                        err = ValueError(f'Premium audio info without duration for {mediasync_id}')
                        current_span = opentelemetry.trace.get_current_span()
                        current_span.record_exception(err)
                    else:
                        try:
                            audio_duration = pendulum.parse(audio_duration).in_seconds()
                        except Exception:
                            err = ValueError(
                                f'Premium audio info with invalid duration for {mediasync_id}'
                            )
                            current_span = opentelemetry.trace.get_current_span()
                            current_span.record_exception(err)
                            audio_duration = None

                    result[mediasync_id] = {
                        'url': mp3_object['url'],
                        'duration': audio_duration,
                    }
        return result


@zope.interface.implementer(zeit.mediaservice.interfaces.IConnection)
def from_product_config():
    conf = zeit.cms.config.package('zeit.mediaservice')
    return Connection(conf['preview-feed-url'])


class Keycloak:
    def __init__(self, client_id, client_secret, discovery_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.discovery_url = discovery_url

    def authenticate(self):
        try:
            url = f'{self.discovery_url}/protocol/openid-connect/token'
            response = requests.post(
                url,
                data={'grant_type': 'client_credentials'},
                auth=(self.client_id, self.client_secret),
            )
            if not response.ok:
                response.raise_for_status()
        except requests.exceptions.RequestException as err:
            current_span = opentelemetry.trace.get_current_span()
            current_span.record_exception(err)
            return None
        return {'Authorization': 'Bearer ' + response.json()['access_token']}


@zope.interface.implementer(zeit.mediaservice.interfaces.IKeycloak)
def keycloak_from_product_config():
    conf = zeit.cms.config.package('zeit.mediaservice')
    return Keycloak(
        conf['client-id'],
        conf['client-secret'],
        conf['discovery-url'],
    )
