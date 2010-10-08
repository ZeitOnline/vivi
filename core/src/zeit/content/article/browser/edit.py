# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.edit.interfaces
import zope.component
import zope.security.proxy


class EditorContents(object):

    @property
    def body(self):
        return zope.component.getMultiAdapter(
            (self.context,
             zope.security.proxy.removeSecurityProxy(
                 self.context.xml['body'])),
            zeit.edit.interfaces.IArea)


