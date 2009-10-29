# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component
import logging
import uuid
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


@zope.component.adapter(ContentUUID)
@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
def properties(context):
    return zeit.connector.interfaces.IWebDAVProperties(context.context, None)


@grokcore.component.subscribe(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def set_uuid_checkin(context, event):
    set_uuid(context)


@grokcore.component.subscribe(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.repository.interfaces.IBeforeObjectAddEvent)
def set_uuid_add(context, event):
    set_uuid(context)


@grokcore.component.subscribe(
    zeit.cms.interfaces.ICMSContent,
    zope.lifecycleevent.IObjectCreatedEvent)
def set_uuid_create(context, event):
    if zope.lifecycleevent.IObjectCopiedEvent.providedBy(event):
        return
    set_uuid(context)


def set_uuid(context):
    content_uuid = zeit.cms.content.interfaces.IUUID(context)
    if content_uuid.id is not None:
        return
    content_uuid.id = '{urn:uuid:%s}' % uuid.uuid4()
    return content_uuid.id


@grokcore.component.subscribe(
    zeit.cms.repository.interfaces.IRepositoryContent,
    zope.lifecycleevent.IObjectCopiedEvent)
def reset_uuid_for_copied_objects(obj, event):
    uuid = zeit.cms.content.interfaces.IUUID(obj)
    if uuid.id is None:
        return
    with zeit.cms.checkout.helper.checked_out(obj) as co:
        uuid = zeit.cms.content.interfaces.IUUID(co)
        uuid.id = None
        # Checkin handler will set the UUID


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
        log.critical('There %s objects for uuid %s. Using first one.' % (
            len(result), uuid))
    unique_id = result[0][0]
    return zeit.cms.interfaces.ICMSContent(unique_id, None)
