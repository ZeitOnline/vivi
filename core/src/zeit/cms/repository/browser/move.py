from urllib.parse import urlparse
from zeit.cms.i18n import MessageFactory as _
import os.path
import zeit.cms.browser.lightbox
import zeit.cms.browser.menu
import zeit.cms.repository.browser.rename
import zeit.cms.repository.interfaces
import zeit.cms.workflow.interfaces
import zope.copypastemove.interfaces
import zope.formlib.form
import zope.interface
import zope.schema


def valid_name(value):
    if not value.startswith('/'):
        return False

    path = os.path.dirname(value)
    filename = os.path.basename(value)
    if not zeit.cms.interfaces.valid_name(filename):
        return False

    try:
        container = zeit.cms.interfaces.ICMSContent(
            zeit.cms.interfaces.ID_NAMESPACE + path[1:])
    except TypeError:
        raise zeit.cms.repository.interfaces.NotFound(
            _('"${name}" not found.', mapping=dict(name=path)))
    if filename in container:
        raise zeit.cms.repository.interfaces.AlreadyExists(
            _('"${name}" already exists.', mapping=dict(name=value)))
    return True


# XXX copy&paste from .rename, not sure if there's something worth extracting


class IMoveSchema(zope.interface.Interface):

    new_name = zope.schema.TextLine(
        title=_('New path'),
        constraint=valid_name)


class Move(zeit.cms.browser.lightbox.Form,
           zeit.cms.repository.browser.rename.RenameGuards):

    form_fields = zope.formlib.form.FormFields(IMoveSchema)

    template = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'move.pt')

    def get_data(self):
        return {'new_name': urlparse(self.context.uniqueId).path}

    @zope.formlib.form.action(_('Move'))
    def rename(self, action, data):
        old_id = self.context.uniqueId
        path = os.path.dirname(data['new_name'])
        new_name = os.path.basename(data['new_name'])
        container = zeit.cms.interfaces.ICMSContent(
            zeit.cms.interfaces.ID_NAMESPACE + path[1:])
        mover = zope.copypastemove.interfaces.IObjectMover(self.context)
        mover.moveTo(container, new_name)

        # Changing the context also properly sets nextURL.
        self.context = container[new_name]
        self.send_message(_('Renamed "${old_name}" to "${new_name}"',
                            mapping=dict(old_name=old_id,
                                         new_name=self.context.uniqueId)))


class MenuItem(zeit.cms.browser.menu.LightboxActionMenuItem,
               zeit.cms.repository.browser.rename.RenameGuards):

    title = _('Move')

    def render(self):
        if (zeit.cms.repository.interfaces.IRepositoryContent.providedBy(
                self.context) and not self.is_folder_with_content):
            return super().render()
        return ''
