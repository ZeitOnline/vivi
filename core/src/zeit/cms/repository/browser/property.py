import html

import zc.table.column
import zc.table.interfaces
import zope.interface

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.listing


@zope.interface.implementer(zc.table.interfaces.ISortableColumn)
class GetterColumn(zc.table.column.GetterColumn):
    pass


class ActionsColumn(zc.table.column.Column):
    def renderCell(self, item, formatter):
        selector = f'copy_{item[0][0]}'
        copy_translation = _('Copy')
        return (
            f'<pre style="display: none" id="{selector}">'
            f'{html.escape(str(item[1]))}'
            f'</pre>'
            f'<button style="display: flex" onclick="'
            f"try{{navigator.clipboard.writeText(document.getElementById('{selector}').textContent);}}"
            f'catch(e){{console.error(e);}}">'
            f'<img src="/fanstatic/zeit.cms/icons/insert.png"/>'
            f'{copy_translation}'
            f'</button>'
        )


class MetadataColumn(GetterColumn):
    def __init__(self):
        super().__init__(title='')

    def cell_formatter(self, value, item, formatter):
        return '<span class="SearchableText">%s</span>' % ' '.join(
            map(str, [item[0][0], item[0][1], item[1]])
        )


class Listing(zeit.cms.browser.listing.Listing):
    title = _('DAV Properties')
    filter_interface = None
    css_class = 'contentListing hasMetadata'

    columns = (
        GetterColumn(title=_('Namespace'), getter=lambda t, c: t[0][1]),
        GetterColumn(title=_('Name'), getter=lambda t, c: t[0][0]),
        GetterColumn(title=_('Value'), getter=lambda t, c: str(t[1])),
        ActionsColumn(title=_('Actions')),
        MetadataColumn(),
    )

    @property
    def content(self):
        return zeit.cms.interfaces.IWebDAVReadProperties(self.context).items()
