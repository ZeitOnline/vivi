from __future__ import absolute_import
import urbanairship
import zeit.push.interfaces
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
