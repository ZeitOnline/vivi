from zeit.cms.content.interfaces import WRITEABLE_ALWAYS
from zeit.cms.i18n import MessageFactory as _
import grokcore.component
import logging
import zeit.cms.checkout.interfaces
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.relation.interfaces
import zeit.cms.syndication.interfaces
import zeit.cms.workflow.interfaces
import zeit.objectlog.interfaces
import zeit.workflow.interfaces
import zeit.workflow.timebased
import zope.component
import zope.interface
import zope.securitypolicy.interfaces


WORKFLOW_NS = zeit.workflow.interfaces.WORKFLOW_NS
logger = logging.getLogger(__name__)


class ContentWorkflow(zeit.workflow.timebased.TimeBasedWorkflow):
    """Adapt ICMSContent to IWorkflow using the "live" data from connector.

    We must read and write properties directly from the DAV to be sure we
    actually can do the transition.
    """

    zope.interface.implements(zeit.workflow.interfaces.IContentWorkflow)
    zope.component.adapts(zeit.cms.interfaces.IEditorialContent)

    zeit.cms.content.dav.mapProperties(
        zeit.workflow.interfaces.IContentWorkflow,
        WORKFLOW_NS,
        ('edited', 'corrected', 'refined',
         'images_added', 'seo_optimized',
         'urgent'),
        writeable=WRITEABLE_ALWAYS)

    def can_publish(self):
        if self.urgent:
            return zeit.cms.workflow.interfaces.CAN_PUBLISH_SUCCESS
        if self.edited and self.corrected:
            return zeit.cms.workflow.interfaces.CAN_PUBLISH_SUCCESS
        self.error_messages = (
            _('publish-preconditions-urgent', mapping=self._error_mapping),)
        return zeit.cms.workflow.interfaces.CAN_PUBLISH_ERROR


@zope.component.adapter(
    zeit.workflow.interfaces.IContentWorkflow,
    zeit.cms.content.interfaces.IDAVPropertyChangedEvent)
def log_workflow_changes(workflow, event):
    if event.field.__name__ not in (
            'edited', 'corrected', 'refined',
            'images_added', 'seo_optimized',
            'urgent'):
        # Only act on certain fields.
        return

    content = workflow.context
    message = _('${name}: ${new_value}',
                mapping=dict(name=event.field.title,
                             old_value=event.old_value,
                             new_value=event.new_value))

    log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
    log.log(content, message)
