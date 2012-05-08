# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.content.interfaces import WRITEABLE_ALWAYS
import grokcore.component
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zope.interface


class Memo(zeit.cms.content.dav.DAVPropertiesAdapter):

    zope.interface.implements(zeit.cms.content.interfaces.IMemo)

    memo = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.IMemo['memo'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'memo', writeable=WRITEABLE_ALWAYS)


@grokcore.component.subscribe(
    zeit.cms.content.interfaces.ISynchronisingDAVPropertyToXMLEvent)
def ignore_private_token(event):
    if event.name == 'memo':
        event.veto()
