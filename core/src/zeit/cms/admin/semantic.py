import zeit.cms.admin.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.workflow.interfaces
import zope.component
import zope.interface


@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.cms.admin.interfaces.IAdjustSemanticPublish)
class AdjustSemanticPublish:

    def __init__(self, context):
        self.context = context

    @property
    def adjust_semantic_publish(self):
        publish = zeit.cms.workflow.interfaces.IPublishInfo(self.context)
        return publish.date_last_published_semantic

    @adjust_semantic_publish.setter
    def adjust_semantic_publish(self, datetime):
        # Remove security, since last_semantic_change and
        # date_last_published_semantic are defined as readonly.
        context = zope.security.proxy.removeSecurityProxy(self.context)

        publish = zeit.cms.workflow.interfaces.IPublishInfo(context)
        publish.date_last_published_semantic = datetime
        # Also adjust state & date of last semantic change, to avoid setting
        # date_last_published_semantic during next publish of context
        semantic = zeit.cms.content.interfaces.ISemanticChange(context)
        semantic.has_semantic_change = False
        semantic.last_semantic_change = datetime

    @property
    def adjust_first_released(self):
        publish = zeit.cms.workflow.interfaces.IPublishInfo(self.context)
        return publish.date_first_released

    @adjust_first_released.setter
    def adjust_first_released(self, datetime):
        context = zope.security.proxy.removeSecurityProxy(self.context)
        publish = zeit.cms.workflow.interfaces.IPublishInfo(context)
        publish.date_first_released = datetime
