# coding: utf8
from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.interfaces
import zope.schema


class ProductSource(zeit.cms.content.sources.ProductSource):
    """Filtered XML source that only includes products with `volume="true"`."""

    def getValues(self, context):
        values = super(ProductSource, self).getValues(context)
        return [x for x in values if x.volume]


class IVolume(zeit.cms.content.interfaces.IXMLContent):

    product = zope.schema.Choice(
        title=_("Product id"),
        # XXX kludgy, we expect a product with this ID to be present in the XML
        # file. We only need to set an ID here, since to read the product we'll
        # ask the source anyway.
        default=zeit.cms.content.sources.Product(u'ZEI'),
        source=ProductSource())

    year = zope.schema.Int(
        title=_("Year"),
        min=1900,
        max=2100)

    volume = zope.schema.Int(
        title=_("Volume"),
        min=1,
        max=53)

    teaserText = zope.schema.Text(
        title=_("Teaser text"),
        required=False,
        max_length=170)
