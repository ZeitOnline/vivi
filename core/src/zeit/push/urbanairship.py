from __future__ import absolute_import
from zeit.push.interfaces import CONFIG_CHANNEL_NEWS, CONFIG_CHANNEL_BREAKING
import json
import logging
import urbanairship
import zeit.push.interfaces
import zeit.push.mobile
import zope.app.appsetup.product


log = logging.getLogger(__name__)


class Connection(zeit.push.mobile.ConnectionBase):

    def __init__(self, android_application_key, android_master_secret,
                 ios_application_key, ios_master_secret, expire_interval):
        super(Connection, self).__init__(expire_interval)
        self.android_application_key = android_application_key
        self.android_master_secret = android_master_secret
        self.ios_application_key = ios_application_key
        self.ios_master_secret = ios_master_secret

    def send(self, text, link, **kw):
        data = self.data(text, link, **kw)

        # We need channels to define the target audience in order to avoid
        # accidental pushes to *all* devices.
        channels = self.get_channel_list(kw.get('channels'))
        if not channels:
            raise ValueError('No channel given to define target audience.')
        audience_channels = {
            'OR': [{'group': self.config['urbanairship-audience-group'],
                    'tag': channel} for channel in channels],
        }

        # The expiration datetime must not contain microseconds, therefore we
        # cannot use `isoformat`.
        expiry = self.expiration_datetime.strftime('%Y-%m-%dT%H:%M:%S')

        # Send android notification.
        android = urbanairship.Airship(
            self.android_application_key,
            self.android_master_secret
        ).create_push()
        android.audience = audience_channels
        android.expiry = expiry
        android.device_types = urbanairship.device_types('android')
        android.notification = {
            'actions': {
                'open': {
                    'type': 'deep_link',
                    'content': data['android']['deep_link']
                }
            },
            'alert': data['android']['alert'],
            'android': {
                'extra': {
                    'headline': data['android']['headline'],
                    'tag': data['android']['tag'],
                    'url': data['android']['url']
                },
                'priority': data['android']['priority'],
                'title': data['android']['headline']
            }
        }
        self.push(android)

        # Send ios notification.
        ios = urbanairship.Airship(
            self.ios_application_key,
            self.ios_master_secret
        ).create_push()
        ios.audience = audience_channels
        ios.expiry = expiry
        ios.device_types = urbanairship.device_types('ios')
        ios.notification = {
            'actions': {
                'open': {
                    'type': 'deep_link',
                    'content': data['ios']['deep_link']
                }
            },
            'alert': data['ios']['alert'],
            'ios': {
                'extra': {
                    'headline': data['ios']['headline'],
                    'tag': data['ios']['tag'],
                    'url': data['ios']['url']
                },
                'sound': data['ios']['sound'],
                'title': data['ios']['headline']
            }
        }
        self.push(ios)

    def push(self, push):
        log.debug('Sending Push to Urban Airship: %s', push.payload)
        try:
            push.send()
        except urbanairship.common.Unauthorized:
            log.error(
                'Semantic error during push to Urban Airship with payload %s',
                push.payload, exc_info=True)
            raise zeit.push.interfaces.WebServiceError('Unauthorized')
        except urbanairship.common.AirshipFailure, e:
            log.error(
                'Technical error during push to Urban Airship with payload %s',
                push.payload, exc_info=True)
            raise zeit.push.interfaces.TechnicalError(str(e))


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
def from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.push')
    return Connection(
        android_application_key=config['urbanairship-android-application-key'],
        android_master_secret=config['urbanairship-android-master-secret'],
        ios_application_key=config['urbanairship-ios-application-key'],
        ios_master_secret=config['urbanairship-ios-master-secret'],
        expire_interval=int(config['urbanairship-expire-interval']))


class PayloadDocumentation(Connection):

    def push(self, data):
        print json.dumps(data.payload, indent=2, sort_keys=True) + ','


def print_payload_documentation():
    zope.app.appsetup.product.setProductConfiguration('zeit.push', {
        CONFIG_CHANNEL_BREAKING: 'Eilmeldung',
        CONFIG_CHANNEL_NEWS: 'News',
        'push-target-url': 'http://www.zeit.de',
        'urbanairship-audience-group': 'subscriptions'
    })
    conn = PayloadDocumentation(
        'android_application_key', 'android_master_secret',
        'ios_application_key', 'ios_master_secret', expire_interval=9000)
    params = {
        'teaserTitle': 'TeaserTitle',
        'teaserText': 'TeaserText',
        'teaserSupertitle': 'TeaserSupertitle',
    }
    print '[{"//": "*** Eilmeldung ***"},'
    conn.send('PushTitle', 'http://www.zeit.de/test/artikel',
              channels=CONFIG_CHANNEL_BREAKING, **params)
    print '\n'
    print '{"//": "*** Wichtige Nachrichten ***"},'
    conn.send('PushTitle', 'http://www.zeit.de/test/artikel',
              channels=CONFIG_CHANNEL_NEWS, **params)
    print ']'
