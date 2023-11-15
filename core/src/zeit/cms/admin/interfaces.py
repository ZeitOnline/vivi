from zeit.cms.i18n import MessageFactory as _
import zeit.cms.interfaces
import zope.interface
import zope.schema


class IAdjustSemanticPublish(zope.interface.Interface):
    """Schema for admin form to adjust date_last_published_semantic.

    Setting date_last_published_semantic to another date is not enough, since
    has_semantic_change and last_semantic_change might need changes as well.
    Therefore we use this separate interface and take care of all attributes in
    one place.

    """

    adjust_semantic_publish = zope.schema.Datetime(
        title=_('Adjust last published with semantic change'),
        required=False,
        max=zeit.cms.interfaces.MAX_PUBLISH_DATE,
    )

    adjust_first_released = zope.schema.Datetime(
        title=_('Adjust first released'), required=False, max=zeit.cms.interfaces.MAX_PUBLISH_DATE
    )


class IAdditionalFields(zope.interface.Interface):
    pass


class IAdditionalFieldsCO(zope.interface.Interface):
    pass
