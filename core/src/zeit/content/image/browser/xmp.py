import zc.table.column
import zc.table.interfaces
import zope.interface

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.listing
import zeit.content.image.xmp


@zope.interface.implementer(zc.table.interfaces.ISortableColumn)
class GetterColumn(zc.table.column.GetterColumn):
    pass


class MetadataColumn(GetterColumn):
    def __init__(self):
        super().__init__(title='')

    def cell_formatter(self, value, item, formatter):
        return '<span class="SearchableText">%s</span>' % ' '.join(map(str, [item[0], item[1]]))


class Listing(zeit.cms.browser.listing.Listing):
    title = _('XMP Metadata')
    filter_interface = None
    css_class = 'contentListing hasMetadata'

    columns = (
        GetterColumn(title=_('Name'), getter=lambda t, c: t[0]),
        GetterColumn(title=_('Value'), getter=lambda t, c: str(t[1])),
        MetadataColumn(),
    )

    @property
    def content(self):
        img = self._image
        if img is None:
            return ()
        return sorted(img.getXMPFlattened().items())

    @property
    def _image(self):
        return self.context


class GroupListing(Listing):
    @property
    def _image(self):
        return self.context.master_image_for_viewport('desktop')
