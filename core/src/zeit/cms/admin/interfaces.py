from zeit.cms.i18n import MessageFactory as _
import zeit.cms.interfaces
import zope.interface
import zope.schema


class IDateBackSemanticPublish(zope.interface.Interface):
    """Schema for admin form to date back date_last_published_semantic.

    Setting date_last_published_semantic to an older date is not enough, since
    last_semantic_change and date_last_published might need changes as well.
    Therefore we use this separate interface and take care of all attributes in
    one place.

    """

    date_back_last_publish_semantic = zope.schema.Datetime(
        title=_('Date back last published with semantic change'),
        description=_('date-back-last-publish-semantic-description'),
        required=False,
        max=zeit.cms.interfaces.MAX_PUBLISH_DATE)
