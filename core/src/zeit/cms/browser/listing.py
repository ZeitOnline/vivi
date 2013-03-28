# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt
"""Directory listing and listing helpers."""

import datetime
import logging

import zc.table.column
import zc.table.table
import zope.app.locking.interfaces
import zope.app.security.interfaces
import zope.component
import zope.interface
import zope.interface.common.idatetime
import zope.viewlet.interfaces

import zeit.cms.browser.interfaces
import zeit.cms.content.sources
from zeit.cms.i18n import MessageFactory as _


logger = logging.getLogger('zeit.cms.browser.listing')


class BaseListRepresentation(object):

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
    def byline(self):
        return self.context.byline

    @zope.cachedescriptors.property.Lazy
    def ressort(self):
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
    def searchableText(self):
        return u' '.join(unicode(v) for v in (
            self.author,
            self.title,
            self.subtitle,
            self.byline,
            self.ressort,
            self.volume,
            self.page,
            self.year,
            self.__name__))


@zope.component.adapter(
    zeit.cms.browser.interfaces.IListRepresentation)
@zope.interface.implementer(zope.app.locking.interfaces.ILockable)
def listRepresentation_to_Lockable(obj):
    return zope.app.locking.interfaces.ILockable(obj.context, None)


class GetterColumn(zc.table.column.GetterColumn):

    zope.interface.implements(zc.table.interfaces.ISortableColumn)

    def cell_formatter(self, value, item, formatter):
        if value is None:
            return u''
        return unicode(value)


class MetadataColumn(GetterColumn):

    def __init__(self, title=u'', searchable_text=True, **kwargs):
        super(MetadataColumn, self).__init__(title=title, **kwargs)
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
        return unicode(value)


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
        formatted = super(FilenameColumn, self).cell_formatter(
            value, item, formatter)
        return u'<span class="filename">%s</span>' % formatted


class HitColumn(GetterColumn):

    def getter(self, item, formatter):
        access_counter = zeit.cms.content.interfaces.IAccessCounter(
            item.context, None)
        if access_counter is None:
            return None
        return access_counter

    def cell_formatter(self, value, item, formatter):
        if value is None:
            return u''

        today, total = value.hits, value.total_hits

        if not total and not today:
            return u''

        if not today:
            today = u'\N{EMPTY SET}'
        if not total:
            total = today

        return '<span class="hitCounter">%s / %s</span>' % (today, total)

    def getSortKey(self, item, formatter):
        counter = self.getter(item, formatter)
        return counter.total_hits, counter.hits


class DatetimeColumn(GetterColumn):

    def cell_formatter(self, value, item, formatter):
        if not value:
            return u''
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
        return value


class Listing(object):
    """Object listing view"""

    title = _('Directory listing')
    types_source = zeit.cms.content.sources.CMSContentTypeSource()
    css_class = 'contentListing hasMetadata'
    filter_interface = None
    no_content_message = _('There are no objects in this folder.')

    columns = (
        TypeColumn(u'', name='type'),
        LockedColumn(u'', name='locked'),
        PublishedColumn(u'', name='published'),
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
        HitColumn(_('Hits')),
        GetterColumn(
            _('Ressort'),
            name='ressort',
            getter=lambda t, c: t.ressort),
        GetterColumn(
            _('Page'),
            name='page',
            getter=lambda t, c: t.page),
        MetadataColumn(u'Metadaten', name='metadata'),
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
