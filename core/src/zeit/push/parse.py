from datetime import datetime, timedelta
import grokcore.component as grok
import json
import logging
import pytz
import requests
import zeit.push.interfaces
import zeit.push.message
import zope.app.appsetup.product as productconfig
import zope.interface


log = logging.getLogger(__name__)


class Connection(object):

    zope.interface.implements(zeit.push.interfaces.IPushNotifier)

    base_url = 'https://api.parse.com/1'

    def __init__(self, application_id, rest_api_key, expire_interval):
        self.application_id = application_id
        self.rest_api_key = rest_api_key
        self.expire_interval = expire_interval

    def send(self, text, link, **kw):
        title = kw.get('title')
        expiration_time = datetime.now(pytz.UTC).replace(
            microsecond=0) + timedelta(seconds=self.expire_interval)
        expiration_time = expiration_time.isoformat()

        parameters = {
            'expiration_time': expiration_time,
        }
        channels = kw.get('channels')
        if channels:
            if not isinstance(channels, list):
                product_config = productconfig.getProductConfiguration(
                    'zeit.push')
                channels = product_config[channels].split(' ')
            if all(channels):
                parameters['channels'] = channels

        android = parameters.copy()
        android.update({
            'where': {'deviceType': 'android'},
            'data': {
                # Parse.com payload
                'alert': text,
                'title': title,
                # App-specific payload
                'url': self.rewrite_url(link),
            }
        })
        self.push(android)

        ios = parameters.copy()
        ios.update({
            'where': {'deviceType': 'ios'},
            'data': {
                # App-specific payload
                'aps': {
                    'alert': text,
                    'alert-title': title,
                    'url': self.rewrite_url(link),
                }
            }
        })
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

    grok.name('parse')
    get_text_from = 'short_text'
