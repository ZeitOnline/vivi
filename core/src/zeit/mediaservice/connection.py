import opentelemetry.trace
import pendulum
import requests
import zope.interface

import zeit.mediaservice.interfaces


class Connection:
    def __init__(self, feed_url):
        self.feed_url = feed_url

    def get_audio_infos(self, year, volume):
        response = requests.get(
            self.feed_url,
            params={'year': year, 'number': volume},
            timeout=2,
        )
        data = response.json()
        result = {}
        for part_of_volume in data['dataFeedElement'][0]['item'].get('hasPart', []):
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
    return Connection(conf['feed-url'])
