from zeit.cms.i18n import MessageFactory as _
import zc.table.column
import zc.table.interfaces
import zeit.cms.browser.listing
import zope.interface


class GetterColumn(zc.table.column.GetterColumn):

    zope.interface.implements(zc.table.interfaces.ISortableColumn)


class MetadataColumn(GetterColumn):

    def __init__(self):
        super(MetadataColumn, self).__init__(title=u'')

    def cell_formatter(self, value, item, formatter):
        return '<span class="SearchableText">%s</span>' % ' '.join(map(str, [
            item[0][0], item[0][1], item[1]]))


class Listing(zeit.cms.browser.listing.Listing):

    title = _('DAV Properties')
    filter_interface = None
    css_class = 'contentListing hasMetadata'

    columns = (
        GetterColumn(
            title=_('Namespace'),
            getter=lambda t, c: t[0][1]),
        GetterColumn(
            title=_('Name'),
            getter=lambda t, c: t[0][0]),
        GetterColumn(
            title=_('Value'),
            getter=lambda t, c: unicode(t[1])),
        MetadataColumn(),
    )

    @property
    def content(self):
        return zeit.cms.interfaces.IWebDAVReadProperties(self.context).items()
