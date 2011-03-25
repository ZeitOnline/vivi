# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.view
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
            entry['tid'] = entry['tid'].encode('base64')

        return dict(
            context_url=self.url(self.context),
            history=history,
            )


class Revert(zeit.edit.browser.view.Action):

    tid = zeit.edit.browser.view.Form('tid')

    def update(self):
        zeit.edit.interfaces.IUndo(
            zope.security.proxy.getObject(self.context)).revert(
            self.tid.decode('base64'))
        self.signal(None, 'reload')
