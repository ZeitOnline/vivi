# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.interfaces
import zeit.edit.browser.view
import zope.lifecycleevent


class SetReference(zeit.edit.browser.view.Action):
    """Drop content object on an IReference."""

    uniqueId = zeit.edit.browser.view.Form('uniqueId')

    def update(self):
        content = zeit.cms.interfaces.ICMSContent(self.uniqueId)
        self.context.references= content
        zope.lifecycleevent.modified(self.context)
        self.signal(
            None, 'reload', self.context.__name__, self.url('@@contents'))

