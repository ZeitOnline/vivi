import logging
import six
import zeit.cms.checkout.helper
import zeit.cms.checkout.interfaces
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.connector.interfaces
import zeit.connector.search
import zope.component
import zope.interface
import zope.lifecycleevent


log = logging.getLogger(__name__)


@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.cms.content.interfaces.IUUID)
class ContentUUID(object):

    id = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.IUUID['id'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'uuid')

    def __init__(self, context):
        self.context = context

    @property
    def shortened(self):
        # Cut off the rather useless 'urn:uuid:' prefix
        if self.id:
            return self.id.strip('{}').replace('urn:uuid:', '')

    def __str__(self):
        return '<%s.%s %s>' % (
            self.__class__.__module__, self.__class__.__name__, self.id)


@zope.component.adapter(ContentUUID)
@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
def properties(context):
    return zeit.connector.interfaces.IWebDAVProperties(context.context, None)


@zope.component.adapter(six.string_types[0])
@zope.interface.implementer(zeit.cms.content.interfaces.IUUID)
class SimpleUUID(object):

    def __init__(self, context):
        self.id = context


@zope.component.adapter(zeit.cms.content.interfaces.IUUID)
@zope.interface.implementer(zeit.cms.interfaces.ICMSContent)
def uuid_to_content(uuid):
    unique_id = resolve_uuid(uuid)
    if not unique_id:
        return None
    return zeit.cms.interfaces.ICMSContent(unique_id, None)


UUID = zeit.connector.search.SearchVar(
    'uuid', zeit.cms.interfaces.DOCUMENT_SCHEMA_NS)


def resolve_uuid(uuid):
    connector = zope.component.getUtility(
        zeit.connector.interfaces.IConnector)
    result = list(connector.search([UUID], UUID == uuid.id))
    if not result:
        return None
    if len(result) > 1:
        log.critical('There are %s objects for uuid %s. Using first one.' % (
            len(result), uuid))
    return result[0][0]
