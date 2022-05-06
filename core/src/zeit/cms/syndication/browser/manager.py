from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import CAN_PUBLISH_SUCCESS
import zc.table.column
import zc.table.table
import zeit.cms.browser.interfaces
import zeit.cms.browser.listing
import zeit.cms.browser.view
import zeit.cms.syndication.interfaces
import zeit.cms.workflow.interfaces
import zope.cachedescriptors.property
import zope.component


class Manager(zeit.cms.browser.view.Base):
    """Syndication manager UI."""

    css_class = 'syndication-manager'

    def update(self):
        if self.request.form:
            targets = self.select_column.getSelected(self.manager.targets,
                                                     self.request)
            if 'syndicate' in self.request.form:
                self.syndicate(targets, hidden=False, hidden_relateds=False)
            elif 'syndicate-wo-hp' in self.request.form:
                self.syndicate(targets, hidden=True, hidden_relateds=False)
            elif 'syndicate-wo-relateds' in self.request.form:
                self.syndicate(targets, hidden=False, hidden_relateds=True)
            elif 'publish' in self.request.form:
                self.publish(targets)
        super().update()

    def has_content(self):
        return self.manager.targets

    def syndicate(self, targets, **kw):
        try:
            self.manager.syndicate(targets, **kw)
        except zeit.cms.syndication.interfaces.SyndicationError as e:
            self.send_message(
                _('Could not syndicate because "${name}" could not be '
                  'locked or checked out.',
                  mapping=dict(name=e.args[0])),
                type="error")
        else:
            target_names = ', '.join(target.__name__ for target in targets)
            self.send_message(_('"${name}" has been syndicated to ${targets}',
                                mapping=dict(
                                    name=self.context.__name__,
                                    targets=target_names)))

    def publish(self, targets):
        for target in targets:
            mapping = dict(
                id=target.uniqueId,
                name=target.__name__)
            info = zeit.cms.workflow.interfaces.IPublishInfo(target)
            if info.can_publish() == CAN_PUBLISH_SUCCESS:
                publish = zeit.cms.workflow.interfaces.IPublish(target)
                publish.publish()
                self.send_message(_('scheduled-for-publishing',
                                    mapping=mapping))
            else:
                self.send_message(_('Could not publish "${name}".',
                                    mapping=mapping),
                                  type='error')

    @zope.cachedescriptors.property.Lazy
    def content(self):
        return zope.component.getMultiAdapter(
            (self.context, self.request),
            zeit.cms.browser.interfaces.IListRepresentation)

    @property
    def manager(self):
        return zeit.cms.syndication.interfaces.ISyndicationManager(
            self.context)

    @property
    def table(self):
        formatter = zc.table.table.FormSortFormatter(
            self.context, self.request, self.manager.targets,
            columns=self.columns)
        formatter.cssClasses['table'] = self.css_class
        return formatter

    @property
    def columns(self):

        return (
            self.select_column,
            zeit.cms.browser.listing.LockedColumn('', name='locked'),
            zc.table.column.GetterColumn(
                _('Title'),
                lambda t, c: t.title),
            zeit.cms.browser.column.LinkColumn(
                title=_('Path'),
                cell_formatter=lambda t, v, f: v.uniqueId),
            zc.table.column.GetterColumn(
                _('Position'),
                lambda t, c: t.getPosition(self.context) or ''),
            zeit.cms.browser.column.LinkColumn(
                hide_header=True,
                sortable=False,
                view='@@show_preview',
                target='_blank',
                cell_formatter=lambda i, v, f: _('Preview')),
        )

    @zope.cachedescriptors.property.Lazy
    def select_column(self):
        return zc.table.column.SelectionColumn(self._id_getter)

    @staticmethod
    def _id_getter(item):
        return item.uniqueId
