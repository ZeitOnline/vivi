from datetime import datetime, timedelta
from zeit.cms.i18n import MessageFactory as _
from zeit.push.interfaces import PARSE_NEWS_CHANNEL, PARSE_BREAKING_CHANNEL
import grokcore.component as grok
import json
import logging
import pytz
import requests
import urllib
import zeit.push.interfaces
import zeit.push.message
import zope.app.appsetup.product
import zope.interface


log = logging.getLogger(__name__)


class Connection(object):

    zope.interface.implements(zeit.push.interfaces.IPushNotifier)

    base_url = 'https://api.parse.com/1'

    # Channels, introduced in VIV-466.
    ANDROID_CHANNEL_VERSION = '1.1'  # Channels work on versions >= x.
    IOS_CHANNEL_VERSION = '20140514.1'  # Channels work on versions > x.
    # ``headline``, introduced in DEV-698.
    IOS_HEADLINE_VERSION = '20150401'  # Headline works on iOS version >= x.

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
        url = self.rewrite_url(link)
        image_url = kw.get('image_url')
        title = text
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
                'appVersion': {'$gte': self.ANDROID_CHANNEL_VERSION},
                'channels': {'$in': channels}
            },
            'data': {
                'action': self.PUSH_ACTION_ID,
                'headline': headline,
                'text': kw.get('teaserTitle', title),
                'teaser': kw.get('teaserText', ''),
                'url': self.add_tracking(url, channel_name, 'android'),
            }
        }
        if image_url:
            android['data']['imageUrl'] = image_url
        if not all(channels):
            del android['where']['channels']
        self.push(android)

        if channel_name == PARSE_BREAKING_CHANNEL:
            android_legacy = {
                'expiration_time': expiration_time,
                'where': {
                    'deviceType': 'android',
                    'appVersion': {'$lt': self.ANDROID_CHANNEL_VERSION}
                },
                'data': {
                    'alert': title,
                    'title': headline,
                    'url': self.add_tracking(url, channel_name, 'android'),
                }
            }
            self.push(android_legacy)

        if kw.get('skip_ios'):
            # XXX Skipping iOS is for unittests only, since we cannot push to
            # iOS without an Apple certificate.
            return

        ios = {
            'expiration_time': expiration_time,
            'where': {
                'deviceType': 'ios',
                'appVersion': {'$gte': self.IOS_HEADLINE_VERSION},
                'channels': {'$in': channels}
            },
            'data': {
                'aps': {
                    'headline': kw.get('teaserTitle', ''),
                    'alert-title': headline,
                    'alert': kw.get('teaserText', title),
                    'url': self.add_tracking(url, channel_name, 'ios'),
                }
            }
        }
        if image_url:
            ios['data']['aps']['imageUrl'] = image_url
        if not all(channels):
            del ios['where']['channels']
        self.push(ios)

        ios_noheadline = {
            'expiration_time': expiration_time,
            'where': {
                'deviceType': 'ios',
                'appVersion': {'$gt': self.IOS_CHANNEL_VERSION,
                               '$lt': self.IOS_HEADLINE_VERSION},
                'channels': {'$in': channels}
            },
            'data': {
                'aps': {
                    'alert-title': headline,
                    'alert': title,
                    'url': self.add_tracking(url, channel_name, 'ios'),
                }
            }
        }
        if not all(channels):
            del ios_noheadline['where']['channels']
        self.push(ios_noheadline)

        if channel_name == PARSE_BREAKING_CHANNEL:
            ios_legacy = {
                'expiration_time': expiration_time,
                'where': {
                    'deviceType': 'ios',
                    'appVersion': {'$lte': self.IOS_CHANNEL_VERSION}
                },
                'data': {
                    'aps': {
                        'alert': title,
                        'alert-title': headline,
                        'url': self.add_tracking(url, channel_name, 'ios'),
                    }
                }
            }
            self.push(ios_legacy)

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
    def rewrite_url(url):
        is_blog = (
            url.startswith('http://blog.zeit.de')
            or url.startswith('http://www.zeit.de/blog/'))
        url = url.replace('http://www.zeit.de', 'http://wrapper.zeit.de', 1)
        url = url.replace(
            'http://blog.zeit.de', 'http://wrapper.zeit.de/blog', 1)
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


class Message(zeit.push.message.OneTimeMessage):

    grok.context(zeit.cms.content.interfaces.ICommonMetadata)
    grok.name('parse')

    @property
    def text(self):
        """Override to read title of article, instead of short text."""
        return self.context.title

    @property
    def additional_parameters(self):
        result = {}
        for name in ['teaserTitle', 'teaserText', 'teaserSupertitle']:
            value = getattr(self.context, name)
            if value:
                result[name] = value
        if self.image:
            result['image_url'] = self.image.uniqueId.replace(
                zeit.cms.interfaces.ID_NAMESPACE, 'http://images.zeit.de/')
        return result

    @property
    def image(self):
        images = zeit.content.image.interfaces.IImages(self.context, None)
        if images is None or images.image is None:
            return None
        image = images.image
        if zeit.content.image.interfaces.IImageGroup.providedBy(image):
            for name in image:
                if self._image_pattern in name:
                    return image[name]
        else:
            return image

    @property
    def _image_pattern(self):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.push')
        return config['parse-image-pattern']


@grok.subscribe(
    zeit.cms.content.interfaces.ICommonMetadata,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def set_push_news_flag(context, event):
    push = zeit.push.interfaces.IPushMessages(context)
    if not push.enabled:
        return
    for service in push.message_config:
        if (service['type'] == 'parse' and service['enabled']
                and service.get('channels') == PARSE_NEWS_CHANNEL):
            context.push_news = True
            break
