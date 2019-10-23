from zeit.cmp.source import Unknown
from zeit.cms.i18n import MessageFactory as _
import xml.sax.saxutils
import zc.sourcefactory.source
import zeit.cmp.source
import zope.interface
import zope.schema


class VendorSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.cmp'
    config_url = 'vendors'
    attribute = 'id'

    class source_class(zc.sourcefactory.source.FactoredContextualSource):
        def cmp_id(self, value):
            return self.factory.cmp_id(self.context, value)

    def cmp_id(self, context, value):
        tree = self._get_tree()
        nodes = tree.xpath('%s[@%s=%s]' % (
                           self.title_xpath,
                           self.attribute,
                           xml.sax.saxutils.quoteattr(value)))
        return nodes[0].get('cmp') if nodes else None


VENDOR_SOURCE = VendorSource()


class IConsentInfo(zope.interface.Interface):
    """Provides CMP Consent Management Platform related data."""

    has_thirdparty = zope.schema.Choice(
        title=_('Contains thirdparty code'),
        default=Unknown,
        source=zeit.cmp.source.TriState())

    thirdparty_vendors = zope.schema.Tuple(
        title=_('Vendors'),
        value_type=zope.schema.Choice(source=VENDOR_SOURCE),
        default=(),
        required=False,
        unique=True)

    thirdparty_vendors_cmp_ids = zope.interface.Attribute(
        'thirdparty_vendors translated to external CMP IDs')
