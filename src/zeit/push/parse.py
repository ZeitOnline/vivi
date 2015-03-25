from datetime import datetime, timedelta
from zeit.cms.i18n import MessageFactory as _
from zeit.push.interfaces import PARSE_NEWS_CHANNEL, PARSE_BREAKING_CHANNEL
import grokcore.component as grok
import json
import logging
import pytz
import requests
import zeit.push.interfaces
import zeit.push.message
import zope.app.appsetup.product
import zope.interface


log = logging.getLogger(__name__)


class Connection(object):

    zope.interface.implements(zeit.push.interfaces.IPushNotifier)

    base_url = 'https://api.parse.com/1'

    # Channels only work on mobile apps with version greater than or equal to
    # these (see VIV-466).
    MIN_ANDROID_VERSION = '1.1'
    MIN_IOS_VERSION = '20140514.1'

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
        url = self.rewrite_url(link)
        expiration_time = (datetime.now(pytz.UTC).replace(microsecond=0) +
                           timedelta(seconds=self.expire_interval)).isoformat()

        channel_name = kw.get('channels')
        if isinstance(channel_name, list):
            channels = channel_name
        else:
            channels = config.get(channel_name, '').split(' ')

        if config.get(PARSE_NEWS_CHANNEL) in channels:
            title = kw.get('supertitle', _('ZEIT ONLINE:'))
        else:
            title = _('breaking-news-parse-title')
        # There's no i18n in the mobile app, so we translate to a hard-coded
        # language here.
        title = zope.i18n.translate(title, target_language=self.LANGUAGE)

        # Android >= 1.1
        android = {
            'expiration_time': expiration_time,
            'where': {
                'deviceType': 'android',
                'appVersion': {'$gte': self.MIN_ANDROID_VERSION},
                'channels': {'$in': channels}
            },
            'data': {
                'action': self.PUSH_ACTION_ID,
                'headline': title,
                'text': text,
                'url': url,
            }
        }
        if not all(channels):
            del android['where']['channels']
        self.push(android)

        # Android < 1.1
        if channel_name == PARSE_BREAKING_CHANNEL:
            android_legacy = {
                'expiration_time': expiration_time,
                'where': {
                    'deviceType': 'android',
                    'appVersion': {'$lt': self.MIN_ANDROID_VERSION}
                },
                'data': {
                    'alert': text,
                    'title': title,
                    'url': url
                }
            }
            self.push(android_legacy)

        if kw.get('skip_ios'):
            # XXX Skipping iOs is for unittests only, since we cannot push to
            # ios without a apple certificate.
            return

        # iOS > 20140514.1
        ios = {
            'expiration_time': expiration_time,
            'where': {
                'deviceType': 'ios',
                'appVersion': {'$gt': self.MIN_IOS_VERSION},
                'channels': {'$in': channels}
            },
            'data': {
                'aps': {
                    'alert': text,
                    'alert-title': title,
                    'url': url,
                }
            }
        }
        if not all(channels):
            del ios['where']['channels']
        self.push(ios)

        # iOS <= 20140514.1
        if channel_name == PARSE_BREAKING_CHANNEL:
            ios_legacy = {
                'expiration_time': expiration_time,
                'where': {
                    'deviceType': 'ios',
                    'appVersion': {'$lte': self.MIN_IOS_VERSION}
                },
                'data': {
                    'aps': {
                        'alert': text,
                        'alert-title': title,
                        'url': url,
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
        if self.context.supertitle:
            result['supertitle'] = self.context.supertitle
        return result


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
