from __future__ import absolute_import
import grokcore.component as grok
import urbanairship
import zeit.cms.content.interfaces
import zeit.push.interfaces
import zeit.push.message
import zope.app.appsetup.product
import zope.interface


class Connection(object):

    zope.interface.implements(zeit.push.interfaces.IPushNotifier)

    def __init__(self, application_key, master_secret, expire_interval):
        self.application_key = application_key
        self.master_secret = master_secret
        self.expire_interval = expire_interval

    def send(self, text, link, **kw):
        airship = urbanairship.Airship(
            self.application_key, self.master_secret)
        push = airship.create_push()
        push.audience = 'all'
        push.notification = urbanairship.notification(alert='Hello')
        push.device_types = urbanairship.device_types('all')
        return push.send()


class Message(zeit.push.message.Message):

    grok.name('urbanairship')
    grok.context(zeit.cms.content.interfaces.ICommonMetadata)

    @property
    def text(self):
        return self.context.title


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
def from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.push')
    return Connection(
        config['urbanairship-application-key'],
        config['urbanairship-master-secret'],
        int(config['urbanairship-expire-interval']))
