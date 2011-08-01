# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import urllib
import zeit.cms.browser.view
import zeit.edit.browser.view
import zeit.edit.interfaces
import zope.security.proxy


class History(zeit.cms.browser.view.JSON):

    resource_library = 'zeit.edit.styles'
    template = 'history.jsont'

    def json(self):
        history = zeit.edit.interfaces.IUndo(
            zope.security.proxy.getObject(self.context)).history
        for entry in history:
            if entry['description'] is None:
                entry['description'] = '[none]'
            entry['tid'] = urllib.quote(entry['tid'].encode('base64'))

        return dict(
            context_url=self.url(self.context),
            history=history,
            )


class Revert(zeit.edit.browser.view.Action):

    tid = zeit.edit.browser.view.Form('tid')

    def update(self):
        tid = urllib.unquote(self.tid).decode('base64')
        undo = zeit.edit.interfaces.IUndo(
            zope.security.proxy.getObject(self.context))

        for entry in undo.history:
            if entry['tid'] == tid:
                self.undo_description = _(
                    'revert up to "${action}"', mapping=dict(
                        action=entry['description']))
                break

        undo.revert(tid)
        self.signal(None, 'reload')
