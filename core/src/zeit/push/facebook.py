# coding: utf-8
import logging

import grokcore.component as grok

import zeit.push.interfaces
import zeit.push.message


log = logging.getLogger(__name__)


class Message(zeit.push.message.Message):
    grok.name('facebook')

    @property
    def text(self):
        return self.config.get('override_text')

    @property
    def url(self):
        return self.add_query_params(
            super().url,
            wt_zmc='sm.int.zonaudev.facebook.ref.zeitde.redpost.link.x',
            utm_medium='sm',
            utm_source='facebook_zonaudev_int',
            utm_campaign='ref',
            utm_content='zeitde_redpost_link_x',
        )

    @property
    def log_message_details(self):
        return 'Account %s' % self.config.get('account', '-')
