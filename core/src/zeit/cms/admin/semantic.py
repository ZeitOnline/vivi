import zeit.cms.admin.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.workflow.interfaces
import zope.component
import zope.interface


class AdjustSemanticPublish(object):

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(zeit.cms.admin.interfaces.IAdjustSemanticPublish)

    def __init__(self, context):
        self.context = context

    @property
    def adjust_semantic_publish(self):
        return zeit.cms.workflow.interfaces.IPublishInfo(
            self.context).date_last_published_semantic

    @adjust_semantic_publish.setter
    def adjust_semantic_publish(self, datetime):
        # Remove security, since last_semantic_change and
        # date_last_published_semantic are defined as readonly.
        context = zope.security.proxy.removeSecurityProxy(self.context)

        # Adjust date of last semantic publish
        publish_info = zeit.cms.workflow.interfaces.IPublishInfo(context)
        publish_info.date_last_published_semantic = datetime

        # Also adjust state & date of last semantic change, to avoid setting
        # date_last_published_semantic during next publish of context
        semantic = zeit.cms.content.interfaces.ISemanticChange(context)
        semantic.has_semantic_change = False
        semantic.last_semantic_change = datetime
