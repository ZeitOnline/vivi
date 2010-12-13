# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.connector.interfaces
import zeit.content.portraitbox.interfaces
import zope.component
import zope.interface


class PortraitboxReference(object):

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(
        zeit.content.portraitbox.interfaces.IPortraitboxReference)

    portraitbox = zeit.cms.content.dav.DAVProperty(
        zeit.content.portraitbox.interfaces.IPortraitboxReference[
            'portraitbox'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'artbox_portrait')

    def __init__(self, context):
        self.context = context


@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
@zope.component.adapter(PortraitboxReference)
def portraitbox_reference_to_webdav_properties(context):
    return zeit.connector.interfaces.IWebDAVProperties(context.context)
