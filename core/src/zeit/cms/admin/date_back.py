import zeit.cms.admin.interfaces
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
    def date_back_last_publish_semantic(self, value):
        # TODO actually change all fields that require changing
        # CAUTION: Cannot just write on IPublishInfo, since fields are readonly
        pass


@zope.component.adapter(zope.interface.Interface)
@zope.interface.implementer(zeit.cms.admin.interfaces.IDateBackSemanticPublish)
def wrapped_context(context):  # TODO maybe better naming
    return DateBackSemanticPublish(context)
