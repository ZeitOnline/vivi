from zeit.cms.i18n import MessageFactory as _
from zope.cachedescriptors.property import Lazy as cachedproperty
import zeit.cms.browser.lightbox
import zeit.cms.browser.menu
import zeit.cms.repository.interfaces
import zeit.cms.workflow.interfaces
import zope.copypastemove.interfaces
import zope.formlib.form
import zope.interface
import zope.schema


class IRenameSchema(zope.interface.Interface):

    new_name = zope.schema.TextLine(
        title=_('New file name'),
        constraint=zeit.cms.repository.interfaces.valid_name)


class Rename(zeit.cms.browser.lightbox.Form):

    form_fields = zope.formlib.form.FormFields(IRenameSchema)

    template = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'rename-box.pt')

    def get_data(self):
        return dict(new_name=self.context.__name__)

    @zope.formlib.form.action(_('Rename'))
    def rename(self, action, data):
        old_name = self.context.__name__
        new_name = data['new_name']

        container = self.context.__parent__
        renamer = zope.copypastemove.interfaces.IContainerItemRenamer(
            container)
        renamer.renameItem(old_name, new_name)

        # Changing the context also properly sets nextURL.
        self.context = container[new_name]
        self.send_message(_('Renamed "${old_name}" to "${new_name}"',
                            mapping=dict(old_name=old_name,
                                         new_name=new_name)))

    @cachedproperty
    def can_rename(self):
        return not zeit.cms.workflow.interfaces.IPublishInfo(
            self.context).published


class MenuItem(zeit.cms.browser.menu.LightboxActionMenuItem):
    """Rename menu item."""

    title = _('Rename')

    def render(self):
        if (zeit.cms.repository.interfaces.IRepositoryContent.providedBy(
                self.context) and
            not zeit.cms.workflow.interfaces.IPublishInfo(
                self.context).published):
            return super(MenuItem, self).render()
        return ''
