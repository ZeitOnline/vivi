import html

import zc.table.column
import zc.table.interfaces
import zope.interface
import zope.traversing.browser


class LinkColumn(zc.table.column.GetterColumn):
    """A column which displays a link to a value."""

    def __init__(
        self, view='', css_class=None, hide_header=False, sortable=True, target=None, **kw
    ):
        super().__init__(**kw)
        self.view = view
        self.hide_header = hide_header
        if css_class:
            self.css_class = css_class
        if sortable:
            zope.interface.alsoProvides(self, zc.table.interfaces.ISortableColumn)
        self.target = target

    def renderHeader(self, formatter):
        if self.hide_header:
            return ''
        return super().renderHeader(formatter)

    def renderCell(self, item, formatter):
        # Get the target object and compute the URL
        target = self.getter(item, formatter)
        if target is None:
            return ''

        # Get the same display as if a normal column.
        content = html.escape(str(super().renderCell(item, formatter)))

        # Try to get a URL, if we can't then ignore setting up a link.
        try:
            url = zope.component.getMultiAdapter((target, formatter.request), name='absolute_url')()
        except TypeError:
            result = content
        else:
            if self.view:
                url = '%s/%s' % (url, self.view)
            css_class = self.css_class(target, item, formatter) or ''
            if css_class:
                css_class = 'class="%s" ' % css_class
            target = ''
            if self.target:
                target = 'target="%s" ' % self.target
            result = '<a %s%shref="%s">%s</a>' % (target, css_class, url, content)
        return result

    def cell_formatter(self, value, item, formatter):
        return value.title

    def getSortKey(self, item, formatter):
        return self.cell_formatter(self.getter(item, formatter), item, formatter)

    def css_class(self, value, item, formatter):
        return ''
