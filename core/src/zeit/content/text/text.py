# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import persistent
import zope.app.container.contained

import zeit.cms.content.dav
import zeit.content.text.interfaces


class Text(persistent.Persistent,
           zope.app.container.contained.Contained):

    zope.interface.implements(zeit.content.text.interfaces.IText)

    uniqueId = None

    encoding = zeit.cms.content.dav.DAVProperty(
        zeit.content.text.interfaces.IText['encoding'],
        zeit.content.text.interfaces.DAV_NAMESPACE, 'encoding',
        use_default=True)

    def __init__(self, text):
        self.text = text
