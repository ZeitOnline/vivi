from __future__ import absolute_import
from zeit.push.interfaces import PARSE_NEWS_CHANNEL, PARSE_BREAKING_CHANNEL
import urbanairship
import zeit.push.interfaces
import zeit.push.mobile
import zope.app.appsetup.product


class Connection(zeit.push.mobile.ConnectionBase):

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

        # The `urbanairship` library takes care of headers, errors etc.
        airship = urbanairship.Airship(self.application_id, self.rest_api_key)

        # If no channel was given, send notification to all users as fallback.
        audience = 'all'
        if all(channels):
            audience = {
                'or': [{'tag': channel} for channel in channels],
                'group': 'device'
            }

        # The expiration datetime must not contain microseconds, therefore we
        # cannot use `isoformat`.
        expiry = self.expiration_datetime.strftime('%Y-%m-%dT%H:%M:%S')

        # Send android notification.
        android = airship.create_push()
        android.audience = audience
        android.options = {'expiry': expiry}
        android.device_types = ['android']
        android.notification = {'android': {'extra': data['android']}}
        self.push(android)

        # Send ios notification.
        ios = airship.create_push()
        ios.audience = audience
        ios.options = {'expiry': expiry}
        ios.device_types = ['ios']
        ios.notification = {'ios': {'extra': data['ios']}}
        self.push(ios)

    def push(self, push):
        try:
            push.send()
        except urbanairship.common.Unauthorized:
            raise zeit.push.interfaces.WebServiceError('Unauthorized')
        except urbanairship.common.AirshipFailure, e:
            raise zeit.push.interfaces.TechnicalError(str(e))


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
def from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.push')
    return Connection(
        config['urbanairship-application-key'],
        config['urbanairship-master-secret'],
        int(config['urbanairship-expire-interval']))
