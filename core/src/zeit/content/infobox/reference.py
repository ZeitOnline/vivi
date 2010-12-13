# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.connector.interfaces
import zeit.content.infobox.interfaces
import zope.component
import zope.interface


class InfoboxReference(object):

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(
        zeit.content.infobox.interfaces.IInfoboxReference)

    infobox = zeit.cms.content.dav.DAVProperty(
        zeit.content.infobox.interfaces.IInfoboxReference['infobox'],
        'http://namespaces.zeit.de/CMS/document', 'artbox_info')

    def __init__(self, context):
        self.context = context


@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
@zope.component.adapter(InfoboxReference)
def infobox_reference_to_webdav_properties(context):
    return zeit.connector.interfaces.IWebDAVProperties(context.context)
