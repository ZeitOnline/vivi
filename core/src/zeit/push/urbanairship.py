from __future__ import absolute_import
from zeit.push.interfaces import PARSE_NEWS_CHANNEL, PARSE_BREAKING_CHANNEL
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

        # Add tag to payload, so App knows which kind of notification was send.
        # (The audience part was already consumed by the SDK.)
        channels = self.get_channel_list(kw.get('channels'))
        if PARSE_BREAKING_CHANNEL in channels:
            tag = self.config.get(PARSE_BREAKING_CHANNEL)
        else:
            tag = self.config.get(PARSE_NEWS_CHANNEL)

        data['android']['tag'] = tag
        data['ios']['tag'] = tag

        # We need channels to define the target audience in order to avoid
        # accidental pushes to *all* devices.
        if not channels:
            raise ValueError('No channel given to define target audience.')

        audience = {
            'or': [{'tag': channel} for channel in channels],
            'group': self.config['urbanairship-audience-group']
        }

        # The expiration datetime must not contain microseconds, therefore we
        # cannot use `isoformat`.
        expiry = self.expiration_datetime.strftime('%Y-%m-%dT%H:%M:%S')

        # Send android notification.
        android = urbanairship.Airship(
            self.android_application_key,
            self.android_master_secret
        ).create_push()
        android.audience = audience
        android.options = {'expiry': expiry}
        android.device_types = ['android']
        android.notification = {'android': {'extra': data['android']}}
        self.push(android)

        # Send ios notification.
        ios = urbanairship.Airship(
            self.ios_application_key,
            self.ios_master_secret
        ).create_push()
        ios.audience = audience
        ios.options = {'expiry': expiry}
        ios.device_types = ['ios']
        ios.notification = {'ios': {
            'title': data['ios'].pop('alert-title'),
            'alert': data['ios'].pop('alert'),
            'extra': data['ios']
        }}
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
