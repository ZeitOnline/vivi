# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import logging

import zope.component
import zope.cachedescriptors.property
import zope.publisher.interfaces

import zc.table.table
import zc.table.column

import zeit.cms.browser.interfaces
import zeit.cms.browser.listing
import zeit.cms.workingcopy.interfaces

import zeit.cms.syndication.interfaces


logger = logging.getLogger('zeit.cms.syndication.browser.feed')


class OrderedSelectionColumn(zc.table.column.SelectionColumn):
    """Selection Column which allows ordered retrieval."""

    def getItems(self, items, request):
        used_ids = request.get(self.prefix + '.used')
        id_map = dict((self.makeId(item), item) for item in items)
        ordered = []
        for id in used_ids:
            ordered.append(id_map[id])
        return ordered

    def getSelected(self, items, request):
        selected_ids = request.get(self.prefix)
        if not selected_ids:
            return []
        id_map = dict((self.makeId(item), item) for item in items)
        result = []
        for id in selected_ids:
            result.append(id_map[id])
        return result

    def renderCell(self, item, formatter):
        value = self.makeId(item)
        name = '%s:list' % self.prefix
        used_name = '%s.used:list' % self.prefix
        checked = self.get(item)
        checked_html = ''
        if checked:
            checked_html = 'checked="checked"'
        return (
            u'<input type="hidden" name="%s" value="%s" />'
            u'<input type="checkbox" name="%s" value="%s" %s /> ') % (
            used_name, value, name, value, checked_html)

    def input(self, items, request):
        raise NotImplementedError()

    def update(self, items, data):
        raise NotImplementedError()


class FeedListRepresentation(zeit.cms.browser.listing.BaseListRepresentation):
    """Adapter for listing a feed."""

    zope.interface.implements(zeit.cms.browser.interfaces.IListRepresentation)
    zope.component.adapts(zeit.cms.syndication.interfaces.IFeed,
                          zope.publisher.interfaces.IPublicationRequest)

    @property
    def title(self):
        return self.context.title

    @property
    def searchableText(self):
        return self.title

    @property
    def metadata(self):
        id = self.context.__name__
        return ('<span class="Metadata">%s</span><span'
                ' class="DeleteId">%s</span>' %(item.url, id))

    year = page = volume = ressort = workflowState = modifiedBy = author = None


class FeedView(object):

    def pinned(self, item):
        return self.context.pinned(item.context)

    @zope.cachedescriptors.property.Lazy
    def title(self):
        return "Inhalt des Feeds: %s" % self.context.title

    @property
    def content(self):
        result = []
        for obj in self.context:
            list_repr = zope.component.queryMultiAdapter(
                (obj, self.request),
                zeit.cms.browser.interfaces.IListRepresentation)
            if list_repr is None:
                # XXX: this codepath is not tested
                logger.warning("Could not adapt %r to IListRepresentation",
                               (obj, ))
            else:
                result.append(list_repr)
        return result

    @property
    def contentTable(self):
        """Returns table listing contents"""
        formatter = zc.table.table.Formatter(
            self.context, self.request, self.content,
            columns=self.columns)
        formatter.cssClasses['table'] = 'feedsorting'
        return formatter

    @property
    def columns(self):

        def _id_getter(item):
            return item.context.uniqueId

        def _url_formatter(value, item, formatter):
            return u'<a href="%s">%s</a>' % (item.url, value)

        return (
            OrderedSelectionColumn(
                _id_getter, getter=self.pinned,
                title=u"Pin"),
            zeit.cms.browser.listing.TypeColumn(u''),
            zc.table.column.GetterColumn(
                u'Autor',
                lambda t, c: t.author),
            zc.table.column.GetterColumn(
                u'Titel',
                lambda t, c: t.title,
                cell_formatter=_url_formatter),
            zc.table.column.GetterColumn(
                u'Position',
                lambda t, c: self.context.getPosition(t.context) or '')
        )


class EditFeedView(FeedView):

    def __call__(self):
        render = super(EditFeedView, self).__call__
        if self.request.form:
            self.updateFeed()
        return render()

    def updateFeed(self):
        content = self.content
        column = self.columns[0]
        orderd_objects = column.getItems(content, self.request)
        orderd_ids = [obj.context.uniqueId for obj in orderd_objects]
        self.context.updateOrder(orderd_ids)

        selected = set(column.getSelected(content, self.request))
        for obj in content:
            if obj in selected:
                self.context.pin(obj.context)
            else:
                self.context.unpin(obj.context)


class AddToMyTargets(object):

    def __call__(self):
        self.add_to_targets()
        url = zope.component.getMultiAdapter(
            (self.context, self.request),
            name='absolute_url')()
        self.request.response.redirect(url)
        return ''

    def add_to_targets(self):
        if self.context not in self.my_targets.targets:
            self.my_targets.targets += (self.context, )

    @zope.cachedescriptors.property.Lazy
    def my_targets(self):
        return zeit.cms.syndication.interfaces.IMySyndicationTargets(
            zeit.cms.workingcopy.interfaces.IWorkingcopy(
                self.request.principal))
