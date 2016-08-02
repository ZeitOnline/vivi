from datetime import datetime, timedelta
from zeit.cms.i18n import MessageFactory as _
from zeit.push.interfaces import PARSE_NEWS_CHANNEL, PARSE_BREAKING_CHANNEL
import grokcore.component as grok
import json
import logging
import pytz
import requests
import urllib
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.push.interfaces
import zeit.push.message
import zope.app.appsetup.product
import zope.interface


log = logging.getLogger(__name__)


class Connection(object):

    zope.interface.implements(zeit.push.interfaces.IPushNotifier)

    base_url = 'https://api.parse.com/1'

    # New link address, introduced in DEV-938.
    ANDROID_FRIEDBERT_VERSION = '1.4'  # New links required on versions >= x.
    IOS_FRIEDBERT_VERSION = '20150914'  # New links required on versions >= x.

    PUSH_ACTION_ID = 'de.zeit.online.PUSH'

    LANGUAGE = 'de'

    def __init__(self, application_id, rest_api_key, expire_interval):
        self.application_id = application_id
        self.rest_api_key = rest_api_key
        self.expire_interval = expire_interval

    def send(self, text, link, **kw):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.push') or {}

        # Determine common payload attributes.
        channel_name = kw.get('channels')
        if isinstance(channel_name, list):
            channels = channel_name
        else:
            channels = config.get(channel_name, '').split(' ')
        friedbert_url = self.rewrite_url(link, 'http://www.zeit.de')
        image_url = kw.get('image_url')
        title = text
        override_text = kw.get('override_text')
        expiration_time = (datetime.now(pytz.UTC).replace(microsecond=0) +
                           timedelta(seconds=self.expire_interval)).isoformat()

        if config.get(PARSE_NEWS_CHANNEL) in channels:
            headline = _('parse-news-title')
        else:
            headline = _('parse-breaking-title')
        # There's no i18n in the mobile app, so we translate to a hard-coded
        # language here.
        headline = zope.i18n.translate(
            headline, target_language=self.LANGUAGE)

        android = {
            'expiration_time': expiration_time,
            'where': {
                'deviceType': 'android',
                'appVersion': {'$gte': self.ANDROID_FRIEDBERT_VERSION},
                'channels': {'$in': channels}
            },
            'data': {
                'action': self.PUSH_ACTION_ID,
                'headline': headline,
                'text': override_text or kw.get('teaserTitle', title),
                'teaser': kw.get('teaserText', ''),
                'url': self.add_tracking(
                    friedbert_url, channel_name, 'android'),
            }
        }
        if image_url:
            android['data']['imageUrl'] = image_url
        if not all(channels):
            del android['where']['channels']
        self.push(android)

        if kw.get('skip_ios'):
            # XXX Skipping iOS is for unittests only, since we cannot push to
            # iOS without an Apple certificate.
            return

        ios = {
            'expiration_time': expiration_time,
            'where': {
                'deviceType': 'ios',
                'appVersion': {'$gte': self.IOS_FRIEDBERT_VERSION},
                'channels': {'$in': channels}
            },
            'data': {
                'aps': {
                    'headline': kw.get('teaserSupertitle', ''),
                    'alert-title': headline,
                    'alert': override_text or kw.get('teaserTitle', title),
                    'teaser': kw.get('teaserText', ''),
                    'url': self.add_tracking(
                        friedbert_url, channel_name, 'ios'),
                }
            }
        }
        if image_url:
            ios['data']['aps']['imageUrl'] = image_url
        if not all(channels):
            del ios['where']['channels']
        self.push(ios)

    def push(self, data):
        headers = {
            'X-Parse-Application-Id': self.application_id,
            'X-Parse-REST-API-Key': self.rest_api_key,
            'Content-Type': 'application/json',
        }
        log.debug('Sending %s', data)
        response = requests.post(
            '%s/push' % self.base_url, data=json.dumps(data), headers=headers)

        if 200 <= response.status_code < 400:
            return
        if response.status_code < 500:
            error = response.json()
            message = error['error']
            if 'code' in error:
                message += ' (code=%s)' % error['code']
            raise zeit.push.interfaces.WebServiceError(message)
        raise zeit.push.interfaces.TechnicalError(response.text)

    @staticmethod
    def rewrite_url(url, target_host):
        is_blog = (
            url.startswith('http://blog.zeit.de')
            or url.startswith('http://www.zeit.de/blog/'))
        url = url.replace('http://www.zeit.de', target_host, 1)
        url = url.replace('http://blog.zeit.de', target_host + '/blog', 1)
        if is_blog:
            url += '?feed=articlexml'
        return url

    @staticmethod
    def add_tracking(url, channel, device):
        if channel == PARSE_BREAKING_CHANNEL:
            channel = 'eilmeldung'
        else:
            channel = 'wichtige_news'
        if device == 'android':
            device = 'andpush'
        else:
            device = 'iospush'

        tracking = {
            'wt_zmc':
            'fix.int.zonaudev.push.{channel}.zeitde.{device}.link.x'.format(
                channel=channel, device=device),
            'utm_medium': 'fix',
            'utm_source': 'push_zonaudev_int',
            'utm_campaign': channel,
            'utm_content': 'zeitde_{device}_link_x'.format(device=device),
        }
        tracking = urllib.urlencode(tracking)
        if '?' in url:
            return url + '&' + tracking
        else:
            return url + '?' + tracking


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
def from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.push')
    return Connection(
        config['parse-application-id'], config['parse-rest-api-key'],
        int(config['parse-expire-interval']))


class PayloadDocumentation(Connection):

    def push(self, data):
        print json.dumps(data, indent=2, sort_keys=True) + ','


def print_payload_documentation():
    zope.app.appsetup.product.setProductConfiguration('zeit.push', {
        PARSE_NEWS_CHANNEL: 'News',
    })
    conn = PayloadDocumentation(
        'application_id', 'rest_api_key', expire_interval=9000)
    params = {
        'teaserTitle': 'TeaserTitle',
        'teaserText': 'TeaserText',
        'teaserSupertitle': 'TeaserSupertitle',
        'image_url': 'http://images.zeit.de/test/image',
    }
    print '[{"//": "*** Eilmeldung ***"},'
    conn.send('Title', 'http://www.zeit.de/test/artikel',
              channels=PARSE_BREAKING_CHANNEL, **params)
    print '\n'
    print '{"//": "*** Wichtige Nachrichten ***"},'
    conn.send('Title', 'http://www.zeit.de/test/artikel',
              channels=PARSE_NEWS_CHANNEL, **params)
    print ']'
