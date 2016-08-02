from __future__ import absolute_import
from zeit.push.interfaces import PARSE_NEWS_CHANNEL, PARSE_BREAKING_CHANNEL
import urbanairship
import zeit.push.interfaces
import zeit.push.mobile
import zope.app.appsetup.product


class Connection(zeit.push.mobile.ConnectionBase):

    def send(self, text, link, **kw):
        data = self.data(text, link, **kw)
        channels = self.get_channel_list(kw.get('channels'))
        if PARSE_BREAKING_CHANNEL in channels:
            tag = self.config.get(PARSE_BREAKING_CHANNEL)
        else:
            tag = self.config.get(PARSE_NEWS_CHANNEL)
        data['android']['tag'] = tag
        data['ios']['tag'] = tag

        airship = urbanairship.Airship(self.application_id, self.rest_api_key)
        android_push = airship.create_push()
        android_push.audience = {
            'or': [{'tag': channel} for channel in channels],
            'group': 'device'
        }
        android_push.device_types = ['android']
        android_push.options = {
            'expiry': self.expiration_datetime.strftime('%Y-%m-%dT%H:%M:%S')}
        android_push.notification = {
            'android': {
                'extra': data['android']
            }
        }
        self.push(android_push)

    def push(self, push):
        push.send()  # might raise unauthorized


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
def from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.push')
    return Connection(
        config['urbanairship-application-key'],
        config['urbanairship-master-secret'],
        int(config['urbanairship-expire-interval']))
