# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import grokcore.view
import zeit.cms.browser.interfaces
import zeit.cms.browser.menu
import zeit.cms.browser.view
import zeit.cms.repository.interfaces
import zeit.purge.interfaces


class Purge(grokcore.view.View,
            zeit.cms.browser.view.Base):

    grokcore.view.context(zeit.cms.repository.interfaces.IRepositoryContent)
    grokcore.view.layer(zeit.cms.browser.interfaces.ICMSLayer)

    def render(self):
        try:
            zeit.purge.interfaces.IPurge(self.context).purge()
        except zeit.purge.interfaces.PurgeError, e:
            self.send_message(
                _('Error while purging ${server}: ${message}',
                  mapping=dict(server=e.server,
                               message=e.message)),
            type='error')
        else:
            self.send_message(_('Purged ${id}', mapping=dict(
                id=self.context.uniqueId)))
        self.redirect(self.url('@@view.html'))


class MenuItem(zeit.cms.browser.menu.ActionMenuItem):

    title = _('Purge')
