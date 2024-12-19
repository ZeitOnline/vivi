# coding: utf8
import zc.sourcefactory.source
import zope.interface
import zope.schema

from zeit.cms.content.interfaces import ICommonMetadata
from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.interfaces
import zeit.cms.content.sources


class ProductSource(zeit.cms.content.sources.ProductSource):
    """
    Filtered XML source that only includes products with `volume="true"`.
    Every product also has dependent Products which are defined in the
    product.xml.
    """

    def getValues(self, context):
        values = super().getValues(context)
        return [value for value in values if value.volume]


PRODUCT_SOURCE = ProductSource()


class IVolume(zeit.cms.content.interfaces.IXMLContent):
    year = ICommonMetadata['year'].bind(object())
    volume = ICommonMetadata['volume'].bind(object())
    # Cannot copy from ICommonMetadata, as we need to change the source here.
    product = zope.schema.Choice(
        title=_('Product id'),
        default=zeit.cms.content.sources.Product('ZEI'),
        source=PRODUCT_SOURCE,
    )

    volume_note = zope.schema.Text(title=_('Volume text'), required=False, max_length=170)

    date_digital_published = zope.schema.Datetime(title=_('Date of digital publication'))

    previous = zope.interface.Attribute(
        'The previous IVolume object (by date_digital_published) or None'
    )
    next = zope.interface.Attribute('The next IVolume object (by date_digital_published) or None')

    title = zope.schema.TextLine(title=_('Title'), required=False)

    teaser = zope.schema.Text(title=_('Teaser'), required=False)

    background_color = zope.schema.TextLine(
        title=_('Area background color (6 characters, no #)'),
        description=_('Hex value of background color for area'),
        required=False,
        min_length=6,
        max_length=6,
        constraint=zeit.cms.content.interfaces.hex_literal,
    )

    def fill_template(text):
        """Fill in a string template with the placeholders year=self.year
        and name=self.volume (zero-padded to two digits), e.g.
        ``http://xml.zeit.de/{year}/{name}/ausgabe``.
        """

    def get_cover(cover_id, product_id, use_fallback):
        """
        Get a cover of a product.
        For example volume.get_cover('printcover','ZEI') returns the
        printcover of DIE ZEIT of this specific volume.
        If no product_id is given or if no Cover is found and use_fallback
        is set, the method looks for a cover of the main_product.
        :param cover_id: str cover ID set in volume-covers.xml
        :param product_id: str product ID set in products.xml
        :param use_fallback: bool specifies if a fallback should be used.
        :return: zeit.content.image.interfaces.IImageGroup or None
        """

    def set_cover(cover_id, product_id, image):
        """
        Set an image as a cover of product.
        """

    def get_cover_title(product_id):
        """
        Get a title of a product.
        For example volume.get_title('ZEI') returns the title of DIE ZEIT of
        this specific volume.
        :param product_id: str product ID set in products.xml
        :return: str
        """

    def set_cover_title(product_id, title):
        """
        Set cover specific title.
        For example volume.set_title('ZEI', 'DIE ZEIT') sets the title of DIE
        ZEIT of this specific volume.
        :param product_id: str product ID set in products.xml
        :param title: str - title of the product
        """

    def all_content_via_search(additional_query_contstraints):
        """
        Get all Content for this volume with a Elasticsearch-Lookup.
        :param additional_query_contstraints: [str] Additional query clauses
        :return: [ICMSContent]
        """

    def change_contents_access(
        access_from, access_to, published, exclude_performing_articles, dry_run
    ):
        """
        Change the access value, from access_from to access_to, for all
        content of this volume and returns the content. The changed content
        wont be published by this method.
        :param access_from: access value to replace
        :param access_to: new acces value
        :param published: bool to specify if only published content should be
               changed
        :param exclude_performing_articles: exclude performing articles from
               change
        :param dry_run: don't actually change the access value
        :return: [CMSContent, ...]
        """

    def content_with_references_for_publishing():
        """
        Looks up all referenced content of relevant content of this volume.
        :return: [ICMSContent, ...]
        """


class IVolumeReference(zeit.cms.content.interfaces.IReference):
    volume_note = IVolume['volume_note'].bind(object())


class ITocConnector(zope.interface.Interface):
    """
    Marker Interface for a the Connector to get the Tocdata from
    /cms/wf-archiv/archiv
    """


class VolumeSource(zeit.cms.content.contentsource.CMSContentSource):
    check_interfaces = (IVolume,)
    name = 'volume'


VOLUME_SOURCE = VolumeSource()


class VolumeCoverSource(zeit.cms.content.sources.XMLSource):
    class source_class(zc.sourcefactory.source.FactoredContextualSource):
        def title(self, id):
            """Expose the `getTitle` function directly on the source class."""
            return self.factory.getTitle(self.context, id)

    product_configuration = 'zeit.content.volume'
    config_url = 'volume-cover-source'
    default_filename = 'volume-covers.xml'
    attribute = 'id'


VOLUME_COVER_SOURCE = VolumeCoverSource()


class AccessControlConfig(zeit.cms.content.sources.CachedXMLBase):
    product_configuration = 'zeit.content.volume'
    config_url = 'access-control-config'
    default_filename = 'volume_access_configuration.xml'

    @property
    def min_cr(self):
        return float(self._find('min_cr') or 0)

    @property
    def min_orders(self):
        return int(self._find('min_orders') or 0)

    def _find(self, name):
        try:
            return getattr(self._get_tree(), name).text
        except Exception:
            return None


ACCESS_CONTROL_CONFIG = AccessControlConfig()
