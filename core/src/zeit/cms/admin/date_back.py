import zeit.cms.admin.interfaces
import zeit.cms.content.interfaces
import zeit.cms.workflow.interfaces
import zope.component
import zope.interface


class DateBackSemanticPublish(object):

    zope.interface.implements(
        zeit.cms.admin.interfaces.IDateBackSemanticPublish)

    def __init__(self, context):
        self.context = context

    @property
    def date_back_last_publish_semantic(self):
        return zeit.cms.workflow.interfaces.IPublishInfo(
            self.context).date_last_published_semantic

    @date_back_last_publish_semantic.setter
    def date_back_last_publish_semantic(self, datetime):
        # Remove security, since last_semantic_change and
        # date_last_published_semantic are defined as readonly.
        context = zope.security.proxy.removeSecurityProxy(self.context)

        semantic = zeit.cms.content.interfaces.ISemanticChange(context)
        semantic.has_semantic_change = False
        semantic.last_semantic_change = datetime

        publish_info = zeit.cms.workflow.interfaces.IPublishInfo(context)
        publish_info.date_last_published_semantic = datetime


@zope.component.adapter(zope.interface.Interface)
@zope.interface.implementer(zeit.cms.admin.interfaces.IDateBackSemanticPublish)
def wrapped_context(context):  # TODO maybe better naming
    return DateBackSemanticPublish(context)
