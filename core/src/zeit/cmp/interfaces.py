from zeit.cmp.source import Unknown
from zeit.cms.i18n import MessageFactory as _
import zeit.cmp.source
import zope.interface
import zope.schema


class IConsentInfo(zope.interface.Interface):
    """Provides CMP Consent Management Platform related data."""

    has_thirdparty = zope.schema.Choice(
        title=_('Contains thirdparty code'),
        default=Unknown,
        source=zeit.cmp.source.TriState())
