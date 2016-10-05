from zeit.push.interfaces import PARSE_NEWS_CHANNEL, PARSE_BREAKING_CHANNEL
import json
import logging
import requests
import zeit.push.interfaces
import zeit.push.message
import zeit.push.mobile
import zope.app.appsetup.product
import zope.interface


log = logging.getLogger(__name__)


class Connection(zeit.push.mobile.ConnectionBase):

    base_url = 'https://api.parse.com/1'

    # New link address, introduced in DEV-938.
    ANDROID_FRIEDBERT_VERSION = '1.4'  # New links required on versions >= x.
    IOS_FRIEDBERT_VERSION = '20150914'  # New links required on versions >= x.

    def __init__(self, application_id, rest_api_key, expire_interval):
        super(Connection, self).__init__(expire_interval)
        self.application_id = application_id
        self.rest_api_key = rest_api_key

    def send(self, text, link, **kw):
        data = self.data(text, link, **kw)
        channels = self.get_channel_list(kw.get('channels'))
        android = {
            'expiration_time': self.expiration_datetime.isoformat(),
            'where': {
                'deviceType': 'android',
                'appVersion': {'$gte': self.ANDROID_FRIEDBERT_VERSION},
                'channels': {'$in': channels}
            },
            'data': data['android']
        }
        if not channels:
            del android['where']['channels']
        self.push(android)

        if kw.get('skip_ios'):
            # XXX Skipping iOS is for unittests only, since we cannot push to
            # iOS without an Apple certificate.
            return

        ios = {
            'expiration_time': self.expiration_datetime.isoformat(),
            'where': {
                'deviceType': 'ios',
                'appVersion': {'$gte': self.IOS_FRIEDBERT_VERSION},
                'channels': {'$in': channels}
            },
            'data': {
                'aps': data['ios']
            }
        }
        if not channels:
            del ios['where']['channels']
        self.push(ios)

    def push(self, data):
        log.debug('Sending Push to Parse: %s', data)
        headers = {
            'X-Parse-Application-Id': self.application_id,
            'X-Parse-REST-API-Key': self.rest_api_key,
            'Content-Type': 'application/json',
        }
        response = requests.post(
            '%s/push' % self.base_url, data=json.dumps(data), headers=headers)

        if 200 <= response.status_code < 400:
            return
        if response.status_code < 500:
            error = response.json()
            message = error['error']
            if 'code' in error:
                message += ' (code=%s)' % error['code']
            log.error('Semantic error during push to Parse with payload %s. '
                      'Response: %s', data, error)
            raise zeit.push.interfaces.WebServiceError(message)
        log.error('Technical error during push to Parse with payload %s. '
                  'Response: %s', data, response.text)
        raise zeit.push.interfaces.TechnicalError(response.text)


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
def from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.push')
    return Connection(
        application_id=config['parse-application-id'],
        rest_api_key=config['parse-rest-api-key'],
        expire_interval=int(config['parse-expire-interval']))


class PayloadDocumentation(Connection):

    def push(self, data):
        print json.dumps(data, indent=2, sort_keys=True) + ','


def print_payload_documentation():
    zope.app.appsetup.product.setProductConfiguration('zeit.push', {
        PARSE_BREAKING_CHANNEL: 'Eilmeldung',
        PARSE_NEWS_CHANNEL: 'News',
        'mobile-target-host': 'http://www.zeit.de',
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
