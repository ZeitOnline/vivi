from zeit.cms.i18n import MessageFactory as _
from zeit.cms.interfaces import ITypeDeclaration
from zeit.cms.repository.folder import FolderType
from zope.cachedescriptors.property import Lazy as cachedproperty
import zeit.cms.browser.lightbox
import zeit.cms.browser.menu
import zeit.cms.repository.interfaces
import zeit.cms.workflow.interfaces
import zope.copypastemove.interfaces
import zope.formlib.form
import zope.interface
import zope.schema
import zope.app.pagetemplate.viewpagetemplatefile


class IRenameSchema(zope.interface.Interface):
    new_name = zope.schema.TextLine(
        title=_('New file name'), constraint=zeit.cms.repository.interfaces.valid_name
    )


class RenameGuards:
    @cachedproperty
    def is_published(self):
        return zeit.cms.workflow.interfaces.IPublishInfo(self.context).published

    @cachedproperty
    def is_folder_with_content(self):
        # Cannot use IFolder.providedBy since that's also true for IImageGroup
        typ = getattr(ITypeDeclaration(self.context, None), 'type_identifier', 'unknown')
        return typ == FolderType.type and len(self.context)


class Rename(zeit.cms.browser.lightbox.Form, RenameGuards):
    form_fields = zope.formlib.form.FormFields(IRenameSchema)

    template = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile('rename-box.pt')

    def get_data(self):
        return {'new_name': self.context.__name__}

    @zope.formlib.form.action(_('Rename'))
    def rename(self, action, data):
        old_name = self.context.__name__
        new_name = data['new_name']

        container = self.context.__parent__
        renamer = zope.copypastemove.interfaces.IContainerItemRenamer(container)
        renamer.renameItem(old_name, new_name)

        # Changing the context also properly sets nextURL.
        self.context = container[new_name]
        self.send_message(
            _(
                'Renamed "${old_name}" to "${new_name}"',
                mapping={'old_name': old_name, 'new_name': new_name},
            )
        )


class MenuItem(zeit.cms.browser.menu.LightboxActionMenuItem, RenameGuards):
    """Rename menu item."""

    title = _('Rename')

    def render(self):
        if (
            zeit.cms.repository.interfaces.IRepositoryContent.providedBy(self.context)
            and not self.is_published
            and not self.is_folder_with_content
        ):
            return super().render()
        return ''
