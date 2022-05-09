from zeit.cms.i18n import MessageFactory as _
import datetime
import logging
import zc.table.column
import zc.table.table
import zeit.cms.browser.interfaces
import zeit.cms.content.sources
import zope.app.locking.interfaces
import zope.app.security.interfaces
import zope.component
import zope.interface
import zope.interface.common.idatetime
import zope.viewlet.interfaces


logger = logging.getLogger('zeit.cms.browser.listing')


class BaseListRepresentation:

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def __parent__(self):
        return self.context.__parent__

    @property
    def __name__(self):
        return self.context.__name__

    @zope.cachedescriptors.property.Lazy
    def uniqueId(self):
        return self.context.uniqueId

    @zope.cachedescriptors.property.Lazy
    def url(self):
        return zope.component.getMultiAdapter(
            (self.context, self.request),
            name='absolute_url')

    @property
    def modifiedOn(self):
        return self._dc_date_helper('modified')

    @property
    def createdOn(self):
        return self._dc_date_helper('created')

    def _dc_date_helper(self, attribute):
        try:
            times = zope.dublincore.interfaces.IDCTimes(
                self.context)
        except TypeError:
            return None
        return getattr(times, attribute)

    @property
    def type(self):
        type_decl = zeit.cms.interfaces.ITypeDeclaration(self.context, None)
        if type_decl:
            return type_decl.type_identifier


class CommonListRepresentation(BaseListRepresentation):
    """Common properties of list representations."""

    @zope.cachedescriptors.property.Lazy
    def author(self):
        return ", ".join(self.context.authors)

    @zope.cachedescriptors.property.Lazy
    def title(self):
        return self.context.title

    @zope.cachedescriptors.property.Lazy
    def subtitle(self):
        return self.context.subtitle

    @zope.cachedescriptors.property.Lazy
    def supertitle(self):
        return self.context.supertitle

    @zope.cachedescriptors.property.Lazy
    def byline(self):
        return self.context.byline

    @zope.cachedescriptors.property.Lazy
    def ressort(self):
        return self.context.ressort

    @zope.cachedescriptors.property.Lazy
    def printRessort(self):
        if self.context.printRessort:
            return self.context.printRessort
        return self.context.ressort

    @zope.cachedescriptors.property.Lazy
    def volume(self):
        return self.context.volume

    @zope.cachedescriptors.property.Lazy
    def page(self):
        return self.context.page

    @zope.cachedescriptors.property.Lazy
    def year(self):
        return self.context.year

    @zope.cachedescriptors.property.Lazy
    def access(self):
        return self.context.access

    @zope.cachedescriptors.property.Lazy
    def workflow(self):
        return zeit.cms.workflow.interfaces.IPublishInfo(self.context)

    @zope.cachedescriptors.property.Lazy
    def teaserimage(self):
        import zeit.content.image.interfaces
        return zeit.content.image.interfaces.IImages(
            self.context).image

    @zope.cachedescriptors.property.Lazy
    def searchableText(self):
        items = []
        for name in ('author', 'title', 'subtitle', 'byline',
                     'ressort', 'volume', 'page', 'year', '__name__'):
            try:
                items.append(str(getattr(self, name)))
            except Exception:
                continue
        return ' '.join(items)


@zope.component.adapter(
    zeit.cms.browser.interfaces.IListRepresentation)
@zope.interface.implementer(zope.app.locking.interfaces.ILockable)
def listRepresentation_to_Lockable(obj):
    return zope.app.locking.interfaces.ILockable(obj.context, None)


@zope.interface.implementer(zc.table.interfaces.ISortableColumn)
class GetterColumn(zc.table.column.GetterColumn):

    def __init__(self, *args, **kw):
        self._getter = kw.pop('getter', None)
        cell_formatter = kw.pop('cell_formatter', None)
        if cell_formatter is not None:
            self.cell_formatter = cell_formatter
        self.sort_default = kw.pop('sort_default', '')
        # Skip immediate superclass and its assignments
        super(zc.table.column.GetterColumn, self).__init__(*args, **kw)

    def getter(self, item, formatter):
        if self._getter is None:
            return super().getter(item, formatter)
        try:
            return self._getter(item, formatter)
        except Exception:
            return None

    def cell_formatter(self, value, item, formatter):
        if value is None:
            return ''
        return str(value)

    def getSortKey(self, item, formatter):
        value = super().getSortKey(item, formatter)
        # XXX `is not None` would feel more correct, but we have unclean data,
        # and for empty string it's the same result in either case.
        return value if value else self.sort_default


class MetadataColumn(GetterColumn):

    def __init__(self, title='', searchable_text=True, **kwargs):
        super().__init__(title=title, **kwargs)
        self.searchable_text = searchable_text

    def getter(self, item, formatter):
        result = []
        if self.searchable_text:
            result.append('<span class="SearchableText">%s</span>' %
                          item.searchableText)
        result.append(
            '<span class="URL">%s</span>'
            '<span class="uniqueId">%s</span>' % (
                item.url, item.uniqueId))
        return ''.join(result)


class LockedColumn(zc.table.column.GetterColumn):

    def getter(self, item, formatter):
        return zope.component.getMultiAdapter(
            (item, formatter.request), name='get_locking_indicator')

    def cell_formatter(self, value, item, formatter):
        return str(value)


class TypeColumn(GetterColumn):

    def getter(self, item, formatter):
        icon = zope.component.queryMultiAdapter(
            (item.context, formatter.request),
            name='zmi_icon')
        if icon is None:
            return ''
        return icon()


class PublishedColumn(zc.table.column.GetterColumn):

    def getter(self, item, formatter):
        return item.context  # The actual content object, not list_repr

    def cell_formatter(self, value, item, formatter):
        viewlet_manager = zope.component.getMultiAdapter(
            (value, formatter.request, self),
            zope.viewlet.interfaces.IViewletManager,
            name='zeit.cms.workflow-indicator')
        viewlet_manager.update()
        return '<div class="workflow-column">%s</div>' % (
            viewlet_manager.render(),)


class FilenameColumn(GetterColumn):

    def cell_formatter(self, value, item, formatter):
        formatted = super().cell_formatter(
            value, item, formatter)
        return '<span class="filename">%s</span>' % formatted


class DatetimeColumn(GetterColumn):

    def cell_formatter(self, value, item, formatter):
        if not value:
            return ''
        tzinfo = zope.interface.common.idatetime.ITZInfo(formatter.request,
                                                         None)
        if tzinfo is not None:
            value = value.astimezone(tzinfo)

        date_formatter = formatter.request.locale.dates.getFormatter(
            'dateTime', 'medium')
        return date_formatter.format(value)

    def getSortKey(self, item, formatter):
        value = self.getter(item, formatter)
        if isinstance(value, datetime.datetime):
            value = value.timetuple()
        else:
            value = datetime.datetime.min.timetuple()
        return value


class Listing:
    """Object listing view"""

    title = _('Directory listing')
    css_class = 'contentListing hasMetadata'
    filter_interface = None
    no_content_message = _('There are no objects in this folder.')

    columns = (
        TypeColumn('', name='type'),
        LockedColumn('', name='locked'),
        PublishedColumn('', name='published'),
        GetterColumn(
            _('Author'),
            name='author',
            getter=lambda t, c: t.author),
        GetterColumn(
            _('Title'),
            name='title',
            getter=lambda t, c: t.title),
        FilenameColumn(
            _('File name'),
            name='filename',
            getter=lambda t, c: t.__name__),
        DatetimeColumn(
            _('Modified'),
            name='modified',
            getter=lambda t, c: t.modifiedOn),
        GetterColumn(
            _('Ressort'),
            name='ressort',
            getter=lambda t, c: t.ressort),
        GetterColumn(
            _('Page'),
            name='page',
            getter=lambda t, c: t.page,
            sort_default=-1),
        MetadataColumn('Metadaten', name='metadata'),
    )

    @zope.cachedescriptors.property.Lazy
    def contentContext(self):
        return self.context

    @property
    def content(self):
        result = []
        for obj in sorted(
                self.contentContext.values(),
                key=zeit.cms.content.interfaces.IContentSortKey):
            if not self.filter_content(obj):
                continue
            list_repr = zope.component.queryMultiAdapter(
                (obj, self.request),
                zeit.cms.browser.interfaces.IListRepresentation)
            if list_repr is None:
                logger.warning("Could not adapt %r to IListRepresentation",
                               (obj, ))
            else:
                result.append(list_repr)
        return result

    @property
    def contentTable(self):
        """Returns table listing contents"""
        formatter = zc.table.table.FormFullFormatter(
            self.context, self.request, self.content,
            columns=self.columns)
        formatter.cssClasses['table'] = self.css_class
        return formatter

    def filter_content(self, obj):
        if self.filter_interface is not None:
            return self.filter_interface.providedBy(obj)

        # Default is to show content:
        return True
