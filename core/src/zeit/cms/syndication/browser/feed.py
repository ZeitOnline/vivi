from zeit.cms.i18n import MessageFactory as _
import html
import logging
import six
import zc.table.column
import zc.table.table
import zeit.cms.browser.interfaces
import zeit.cms.browser.listing
import zeit.cms.browser.menu
import zeit.cms.browser.view
import zeit.cms.syndication.feed
import zeit.cms.syndication.interfaces
import zeit.cms.workingcopy.interfaces
import zope.cachedescriptors.property
import zope.component
import zope.interface
import zope.publisher.interfaces


logger = logging.getLogger(__name__)


class OrderedSelectionColumn(zc.table.column.SelectionColumn):
    """Selection Column which allows ordered retrieval."""

    widget_extra = ''

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
            u'<input type="checkbox" name="%s" value="%s" %s %s/> ') % (
            used_name, value, name, value, checked_html, self.widget_extra)

    def input(self, items, request):
        raise NotImplementedError()

    def update(self, items, data):
        raise NotImplementedError()


@zope.component.adapter(
    zeit.cms.syndication.interfaces.IFeed,
    zope.publisher.interfaces.IPublicationRequest)
@zope.interface.implementer(zeit.cms.browser.interfaces.IListRepresentation)
class FeedListRepresentation(zeit.cms.browser.listing.BaseListRepresentation):
    """Adapter for listing a feed."""

    @property
    def title(self):
        return self.context.title

    @property
    def searchableText(self):
        return self.title

    year = page = volume = ressort = workflowState = modifiedBy = author = None


class FeedView(object):
    """Sorts, pins and hides from hp."""

    title = _('Feed contents')
    checkbox_widget_extra = 'disabled="disabled"'

    def pinned(self, item):
        return self.context.getMetadata(item.context).pinned

    def visible_on_hp(self, item):
        return not self.context.getMetadata(item.context).hidden

    def big_layout(self, item):
        return self.context.getMetadata(item.context).big_layout

    def visible_relateds(self, item):
        return not self.context.getMetadata(item.context).hidden_relateds

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
        formatter.cssClasses['table'] = 'feedsorting table-sorter'
        return formatter

    @zope.cachedescriptors.property.Lazy
    def columns(self):

        def _url_formatter(value, item, formatter):
            if not value:
                value = item.__name__
            return u'<a href="%s">%s</a>' % (item.url, html.escape(value))

        def _escape(value, item, formatter):
            return html.escape(six.text_type(value))

        return (
            zc.table.column.GetterColumn(
                _('title-position-in-feed', default=u'#'),
                lambda t, c: self.context.getPosition(t.context) or '',
                cell_formatter=_escape),
            self.pinned_column,
            self.visible_on_hp_column,
            self.layout_column,
            self.visible_relateds_column,
            zeit.cms.browser.listing.TypeColumn(u''),
            zc.table.column.GetterColumn(
                _('Author'),
                lambda t, c: t.author,
                cell_formatter=_escape),
            zc.table.column.GetterColumn(
                _('Title'),
                lambda t, c: t.title,
                cell_formatter=_url_formatter),
        )

    @zope.cachedescriptors.property.Lazy
    def pinned_column(self):
        column = OrderedSelectionColumn(
            self._id_getter, getter=self.pinned, prefix='pin',
            title=_("Pinned"))
        column.widget_extra = self.checkbox_widget_extra
        return column

    @zope.cachedescriptors.property.Lazy
    def visible_on_hp_column(self):
        column = zc.table.column.SelectionColumn(
            self._id_getter, getter=self.visible_on_hp, prefix='hp',
            title=_('title-visible-on-hp', default=u'HP'))
        column.widget_extra = self.checkbox_widget_extra
        return column

    @zope.cachedescriptors.property.Lazy
    def layout_column(self):
        column = zc.table.column.SelectionColumn(
            self._id_getter, getter=self.big_layout, prefix='layout',
            title=_("Big"))
        column.widget_extra = self.checkbox_widget_extra
        return column

    @zope.cachedescriptors.property.Lazy
    def visible_relateds_column(self):
        column = zc.table.column.SelectionColumn(
            self._id_getter, getter=self.visible_relateds,
            prefix='visible_relateds', title=_('Relateds'))
        column.widget_extra = self.checkbox_widget_extra
        return column

    @staticmethod
    def _id_getter(item):
        return item.context.uniqueId


class EditFeedView(FeedView):

    title = _('Edit feed contents')
    checkbox_widget_extra = ''

    def __call__(self):
        render = super(EditFeedView, self).__call__
        if self.request.form:
            self.updateFeed()
        return render()

    @zope.cachedescriptors.property.Lazy
    def columns(self):
        columns = list(super(EditFeedView, self).columns)
        columns[1:1] = [self.delete_column]
        return tuple(columns)

    @zope.cachedescriptors.property.Lazy
    def delete_column(self):
        return zc.table.column.SelectionColumn(
            self._id_getter, getter=lambda x: False, prefix='remove',
            title=_('title-remove', default=u'Remove'))

    def updateFeed(self):
        content = self.content

        orderd_objects = self.pinned_column.getItems(content, self.request)
        orderd_ids = [obj.context.uniqueId for obj in orderd_objects]
        self.context.updateOrder(orderd_ids)

        to_remove = set(self.delete_column.getSelected(content, self.request))
        pinned = set(self.pinned_column.getSelected(content, self.request))
        visible_on_hp = set(
            self.visible_on_hp_column .getSelected(content, self.request))
        big_layout = set(self.layout_column.getSelected(content, self.request))
        visible_relateds = set(
            self.visible_relateds_column.getSelected(content, self.request))
        for obj in content:
            if obj in to_remove:
                self.context.remove(obj.context)
                continue
            metadata = self.context.getMetadata(obj.context)
            metadata.pinned = obj in pinned
            metadata.hidden = obj not in visible_on_hp
            metadata.big_layout = obj in big_layout
            metadata.hidden_relateds = obj not in visible_relateds


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
        view = zope.component.getMultiAdapter(
            (self.context, self.request),
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
        view = zope.component.getMultiAdapter(
            (self.context, self.request),
            name='remove-from-my-syndication-targets.html')
        if not view.in_targets:
            return ''
        else:
            return super(RemoveFromMySyndicationTargetsMenuItem, self).render()


@zope.component.adapter(
    zeit.cms.syndication.feed.FakeEntry,
    zeit.cms.browser.interfaces.ICMSLayer)
@zope.interface.implementer(zeit.cms.browser.interfaces.IListRepresentation)
class FakeEntryRepresentation(zeit.cms.browser.listing.BaseListRepresentation):
    """Adapter for listing a feed."""

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
