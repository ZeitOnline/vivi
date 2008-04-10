# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import cgi
import logging

import zope.cachedescriptors.property
import zope.component
import zope.interface
import zope.publisher.interfaces

import zc.table.column
import zc.table.table

import zeit.cms.browser.interfaces
import zeit.cms.browser.listing
import zeit.cms.browser.view
import zeit.cms.browser.menu
import zeit.cms.workingcopy.interfaces
import zeit.cms.syndication.interfaces
from zeit.cms.i18n import MessageFactory as _


logger = logging.getLogger(__name__)


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
    """Sorts, pins and hides from hp."""

    def pinned(self, item):
        return self.context.pinned(item.context)

    def hidden(self, item):
        return self.context.hidden(item.context)

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

    @zope.cachedescriptors.property.Lazy
    def columns(self):

        def _id_getter(item):
            return item.context.uniqueId

        def _url_formatter(value, item, formatter):
            return u'<a href="%s">%s</a>' % (item.url, cgi.escape(value))

        def _escape(value, item, formatter):
            return cgi.escape(unicode(value))

        return (
            OrderedSelectionColumn(
                _id_getter, getter=self.pinned, prefix='pin',
                title=_("Pinned")),
            zc.table.column.SelectionColumn(
                _id_getter, getter=self.hidden, prefix='hide',
                title=_("Hidden on HP")),
            zeit.cms.browser.listing.TypeColumn(u''),
            zc.table.column.GetterColumn(
                _('Author'),
                lambda t, c: t.author,
                cell_formatter=_escape),
            zc.table.column.GetterColumn(
                _('Title'),
                lambda t, c: t.title,
                cell_formatter=_url_formatter),
            zc.table.column.GetterColumn(
                u'Position',
                lambda t, c: self.context.getPosition(t.context) or '',
                cell_formatter=_escape),
            zeit.cms.browser.listing.HitColumn(_('Hits')),
        )


class EditFeedView(FeedView):

    def __call__(self):
        render = super(EditFeedView, self).__call__
        if self.request.form:
            self.updateFeed()
        return render()

    def updateFeed(self):
        content = self.content
        pin_column = self.columns[0]
        hide_column = self.columns[1]

        orderd_objects = pin_column.getItems(content, self.request)
        orderd_ids = [obj.context.uniqueId for obj in orderd_objects]
        self.context.updateOrder(orderd_ids)

        selected = set(pin_column.getSelected(content, self.request))
        hidden = set(hide_column.getSelected(content, self.request))
        for obj in content:
            if obj in selected:
                self.context.pin(obj.context)
            else:
                self.context.unpin(obj.context)
            if obj in hidden:
                self.context.hide(obj.context)
            else:
                self.context.show(obj.context)


class AddToMyTargets(zeit.cms.browser.view.Base):

    def __call__(self):
        self.add_to_targets()
        self.send_message(
            _('"${name}" has been added to your syndication targets.',
              mapping=dict(name=self.context.__name__)))
        self.request.response.redirect(self.url(self.context))
        return ''

    def add_to_targets(self):
        if self.context not in self.my_targets.targets:
            self.my_targets.targets += (self.context, )

    @zope.cachedescriptors.property.Lazy
    def my_targets(self):
        return zeit.cms.syndication.interfaces.IMySyndicationTargets(
            zeit.cms.workingcopy.interfaces.IWorkingcopy(
                self.request.principal))


@zope.component.adapter(zeit.cms.syndication.interfaces.IFeed)
@zope.interface.implementer(zeit.cms.browser.interfaces.IPreviewObject)
def feed_preview(context):
    return context.__parent__.get('index')


class RememberSyndicationTargetMenuItem(zeit.cms.browser.menu.ActionMenuItem):
    """Remember as syndication target menu item"""
