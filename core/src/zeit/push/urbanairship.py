from __future__ import absolute_import
import urbanairship
import zeit.push.interfaces
import zeit.push.mobile
import zope.app.appsetup.product


class Connection(zeit.push.mobile.ConnectionBase):

    def send(self, text, link, **kw):
        data = self.data(text, link, **kw)
        channels = self.get_channel_list(kw.get('channels'))
        self.push(data['android'], channels)

    def push(self, data, channels):
        channel = self.config.get(zeit.push.interfaces.PARSE_NEWS_CHANNEL)
        airship = urbanairship.Airship(self.application_id, self.rest_api_key)
        push = airship.create_push()
        push.audience = {
            'tag': 'News' if channel in channels else 'Eilmeldung',
            'group': 'device'
        }
        push.notification = urbanairship.notification(
            android=urbanairship.android(extra=data))
        push.device_types = urbanairship.device_types('android')
        push.send()  # might raise unauthorized


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
def from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.push')
    return Connection(
        config['urbanairship-application-key'],
        config['urbanairship-master-secret'],
        int(config['urbanairship-expire-interval']))
