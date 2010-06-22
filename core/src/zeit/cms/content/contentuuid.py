# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import logging
import zeit.cms.checkout.interfaces
import zeit.cms.checkout.helper
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.connector.interfaces
import zeit.connector.search
import zope.component
import zope.interface
import zope.lifecycleevent


log = logging.getLogger(__name__)


class ContentUUID(object):

    zope.interface.implements(zeit.cms.content.interfaces.IUUID)
    zope.component.adapts(zeit.cms.interfaces.ICMSContent)

    id = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.IUUID['id'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'uuid')

    def __init__(self, context):
        self.context = context

    def __str__(self):
        return '<%s.%s %s>' % (
            self.__class__.__module__, self.__class__.__name__, self.id)


@zope.component.adapter(ContentUUID)
@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
def properties(context):
    return zeit.connector.interfaces.IWebDAVProperties(context.context, None)


class SimpleUUID(object):

    zope.component.adapts(basestring)
    zope.interface.implements(zeit.cms.content.interfaces.IUUID)

    def __init__(self, context):
        self.id = context


@zope.component.adapter(zeit.cms.content.interfaces.IUUID)
@zope.interface.implementer(zeit.cms.interfaces.ICMSContent)
def uuid_to_content(uuid):
    connector = zope.component.getUtility(
        zeit.connector.interfaces.IConnector)
    uuid_var = zeit.connector.search.SearchVar(
        'uuid', zeit.cms.interfaces.DOCUMENT_SCHEMA_NS)
    result = list(connector.search([uuid_var], uuid_var == uuid.id))
    if not result:
        return None
    if len(result) > 1:
        log.critical('There are %s objects for uuid %s. Using first one.' % (
            len(result), uuid))
    unique_id = result[0][0]
    return zeit.cms.interfaces.ICMSContent(unique_id, None)
