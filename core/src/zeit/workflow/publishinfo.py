# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.content.interfaces import WRITEABLE_LIVE
from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.cms.workflow.interfaces
import zeit.connector.interfaces
import zeit.workflow.interfaces
import zope.component
import zope.interface


class NotPublishablePublishInfo(object):
    """A publish info which indicates that the content is not publishable."""

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(zeit.cms.workflow.interfaces.IPublishInfo)

    zeit.cms.content.dav.mapProperties(
        zeit.cms.workflow.interfaces.IPublishInfo,
        zeit.workflow.interfaces.WORKFLOW_NS,
        ('published', 'date_last_published'),
        use_default=True, writeable=WRITEABLE_LIVE)

    zeit.cms.content.dav.mapProperties(
        zeit.cms.workflow.interfaces.IPublishInfo,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, ('date_first_released',),
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
        return False


@zope.component.adapter(NotPublishablePublishInfo)
@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
def workflowProperties(context):
    return zeit.connector.interfaces.IWebDAVProperties(context.context, None)
