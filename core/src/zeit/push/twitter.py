import logging

import grokcore.component as grok
import zope.container.btree
import zope.interface

import zeit.push.interfaces
import zeit.push.message


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
class Connection:
    pass


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
def from_product_config():
    return Connection()


class Message(zeit.push.message.Message):
    grok.name('twitter')

    @property
    def text(self):
        text = self.config.get('override_text')
        if not text:  # BBB
            self.get_text_from = 'short_text'
            text = super().text
        return text

    @property
    def log_message_details(self):
        return 'Account %s' % self.config.get('account', '-')
