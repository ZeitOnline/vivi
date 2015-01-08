from zeit.cms.content.interfaces import WRITEABLE_LIVE
from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.cms.workflow.interfaces
import zeit.connector.interfaces
import zeit.workflow.interfaces
import zope.authentication.interfaces
import zope.component
import zope.interface


class PublishInfo(object):

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(zeit.cms.workflow.interfaces.IPublishInfo)

    zeit.cms.content.dav.mapProperties(
        zeit.cms.workflow.interfaces.IPublishInfo,
        zeit.workflow.interfaces.WORKFLOW_NS,
        ('published', 'date_last_published', 'date_last_published_semantic'),
        use_default=True, writeable=WRITEABLE_LIVE)

    zeit.cms.content.dav.mapProperties(
        zeit.cms.workflow.interfaces.IPublishInfo,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('date_first_released',),
        writeable=WRITEABLE_LIVE)

    def __init__(self, context):
        self.context = context

    @property
    def last_published_by(self):
        log = zeit.objectlog.interfaces.ILog(self.context)
        for entry in reversed(list(log.get_log())):
            if entry.message == _('Published'):
                return entry.principal
        else:
            return None

    def can_publish(self):
        raise NotImplementedError()


class NotPublishablePublishInfo(PublishInfo):

    def can_publish(self):
        return False


@zope.component.adapter(PublishInfo)
@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
def workflowProperties(context):
    return zeit.connector.interfaces.IWebDAVProperties(context.context, None)


# XXX what's the proper place for this?
# XXX return null object insted of None?
def id_to_principal(principal_id):
    if principal_id is None:
        return None
    auth = zope.component.getUtility(
        zope.authentication.interfaces.IAuthentication)
    try:
        return auth.getPrincipal(principal_id)
    except zope.authentication.interfaces.PrincipalLookupError:
        return None
