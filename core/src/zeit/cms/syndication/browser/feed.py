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
import zeit.cms.syndication.feed
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
            zc.table.column.SelectionColumn(
                _id_getter, getter=lambda x: False, prefix='remove',
                title=_('Remove')),
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
        delete_column = self.columns[0]
        pin_column = self.columns[1]
        hide_column = self.columns[2]

        orderd_objects = pin_column.getItems(content, self.request)
        orderd_ids = [obj.context.uniqueId for obj in orderd_objects]
        self.context.updateOrder(orderd_ids)

        to_remove = set(delete_column.getSelected(content, self.request))
        selected = set(pin_column.getSelected(content, self.request))
        hidden = set(hide_column.getSelected(content, self.request))
        for obj in content:
            if obj in to_remove:
                self.context.remove(obj.context)
                continue
            if obj in selected:
                self.context.pin(obj.context)
            else:
                self.context.unpin(obj.context)
            if obj in hidden:
                self.context.hide(obj.context)
            else:
                self.context.show(obj.context)


class MyTargets(zeit.cms.browser.view.Base):

    def add_to_targets(self):
        if self.context not in self.my_targets:
            self.my_targets.add(self.context)
            self.send_message(
                _('"${name}" has been added to your syndication targets.',
                  mapping=dict(name=self.context.__name__)))
        return self.redirect()

    def remove_from_my_targets(self):
        if self.context in self.my_targets:
            self.my_targets.remove(self.context)
            self.send_message(
                _('"${name}" has been removed from your syndication targets.',
                  mapping=dict(name=self.context.__name__)))
        return self.redirect()

    def redirect(self):
        self.request.response.redirect(self.url(self.context))

    @property
    def in_targets(self):
        return self.context in self.my_targets

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

    title = _('Remember as syndication target')

    def render(self):
        view = zope.component.getMultiAdapter((self.context, self.request),
            name='remove-from-my-syndication-targets.html')
        if view.in_targets:
            return ''
        else:
            return super(RememberSyndicationTargetMenuItem, self).render()


class RemoveFromMySyndicationTargetsMenuItem(
    zeit.cms.browser.menu.ActionMenuItem):
    """Remove from my syndication targets menu item"""

    title = _('Remove from my syndication targets')

    def render(self):
        view = zope.component.getMultiAdapter((self.context, self.request),
            name='remove-from-my-syndication-targets.html')
        if not view.in_targets:
            return ''
        else:
            return super(RemoveFromMySyndicationTargetsMenuItem, self).render()



class FakeEntryRepresentation(zeit.cms.browser.listing.BaseListRepresentation):
    """Adapter for listing a feed."""

    zope.interface.implements(zeit.cms.browser.interfaces.IListRepresentation)
    zope.component.adapts(zeit.cms.syndication.feed.FakeEntry,
                          zeit.cms.browser.interfaces.ICMSLayer)

    @property
    def title(self):
        return self.context.title

    @property
    def searchableText(self):
        return self.title

    @property
    def url(self):
        return self.context.uniqueId

    year = page = volume = ressort = workflowState = modifiedBy = author = None
