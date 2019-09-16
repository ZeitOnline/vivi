from zeit.cmp.source import Unknown
from zeit.cms.i18n import MessageFactory as _
import zeit.cmp.source
import zope.interface
import zope.schema


class VendorSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.cmp'
    config_url = 'vendors'
    attribute = 'id'


class IConsentInfo(zope.interface.Interface):
    """Provides CMP Consent Management Platform related data."""

    has_thirdparty = zope.schema.Choice(
        title=_('Contains thirdparty code'),
        default=Unknown,
        source=zeit.cmp.source.TriState())

    thirdparty_vendors = zope.schema.Tuple(
        title=_('Vendors'),
        value_type=zope.schema.Choice(
            source=VendorSource()),
        default=(),
        required=False)
