# vim:fileencoding=utf-8 encoding=utf8
# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import locale
import logging

import zope.component
import zope.interface
import zope.app.security.interfaces

import zc.table.table
import zc.table.column

import zeit.cms.browser.interfaces
import zeit.cms.content.sources
from zeit.cms.i18n import MessageFactory as _


logger = logging.getLogger('zeit.cms.browser.listing')


class BaseListRepresentation(object):

    type = None

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

    def modifiedOn(self, format=None):
        return self._dc_date_helper('modified', format)

    def createdOn(self, format=None):
        return self._dc_date_helper('created', format)

    def _dc_date_helper(self, attribute, format):
        if format is None:
            format = locale.D_T_FMT
        try:
            date = zope.dublincore.interfaces.IDCTimes(
                self.context).modified
        except TypeError:
            return None
        return date.stftime(format)



class CommonListRepresentation(BaseListRepresentation):
    """Common porperties of list representotions."""

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
            self.year))


class MetadataColumn(zc.table.column.GetterColumn):

    def getter(self, item, formatter):
        return ('<span class="SearchableText">%s</span>'
                '<span class="URL">%s</span>'
                '<span class="uniqueId">%s</span>' % (
                    item.searchableText, item.url, item.uniqueId))


class LockedColumn(zc.table.column.GetterColumn):

    def getter(self, item, formatter):
        lockable = zope.app.locking.interfaces.ILockable(item.context, None)
        if lockable is None:
            return ''
        locked = lockable.locked()
        mylock = locked and lockable.ownLock()
        if mylock:
            img = 'lock-closed-mylock'
            title = 'Von Ihnen gesperrt'
        elif locked:
            img = 'lock-closed'
            authentication = zope.component.getUtility(
                zope.app.security.interfaces.IAuthentication)
            locker = lockable.locker()
            try:
                locker = authentication.getPrincipal(locker).title
            except zope.app.security.interfaces.PrincipalLookupError:
                pass
            title = 'Gesperrt von %s' % lockable.locker()
        else:
            return ''
        return '<img src="/@@/zeit.cms/icons/%s.png" title="%s" />' % (
            img, title)


class TypeColumn(zc.table.column.GetterColumn):

    def getter(self, item, formatter):
        icon = zope.component.queryMultiAdapter(
            (item.context, formatter.request),
            name='zmi_icon')
        if icon is None:
            return ''
        return icon()


class GetterColumn(zc.table.column.GetterColumn):

    zope.interface.implements(zc.table.interfaces.ISortableColumn)

    def cell_formatter(self, value, item, formatter):
        if value is None:
            return u''
        return unicode(value)


class FilenameColumn(GetterColumn):

    def cell_formatter(self, value, item, formatter):
        formatted = super(FilenameColumn, self).cell_formatter(
            value, item, formatter)
        return u'<span class="filename">%s</span>' % formatted


class Listing(object):
    """object listing view"""

    title = u"Dateiliste"
    types_source = zeit.cms.content.sources.CMSContentTypeSource()
    css_class = 'contentListing hasMetadata'
    filter_interface = None

    columns = (
        TypeColumn(u'', name='type'),
        LockedColumn(u'', name='locked'),
        GetterColumn(
            _('Author'),
            lambda t, c: t.author),
        GetterColumn(
            _('Titel'),
            lambda t, c: t.title),
        FilenameColumn(
            _('Filename'),
            lambda t, c: t.__name__),
        GetterColumn(
            _('Ressort'),
            lambda t, c: t.ressort),
        GetterColumn(
            _('Year'),
            lambda t, c: t.year),
        GetterColumn(
            _('volme-abbreviated', default=u'Vol.'),
            lambda t, c: t.volume),
        GetterColumn(
            _('Page'),
            lambda t, c: t.page),
        MetadataColumn(u'Metadaten', name='metadata'),
    )

    def __call__(self, *args, **kw):
        return super(Listing, self).__call__(*args, **kw)

    @zope.cachedescriptors.property.Lazy
    def contentContext(self):
        return self.context

    @property
    def content(self):
        result = []
        for obj in self.contentContext.values():
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
        if self.filter_source is not None:
            return obj in self.filter_source

        # Default is to show content:
        return True

    @zope.cachedescriptors.property.Lazy
    def filter_source(self):
        source_name = self.request.get('type_filter')
        if not source_name:
            return None
        return zope.component.getUtility(
            zeit.cms.content.interfaces.ICMSContentSource,
            name=source_name)
