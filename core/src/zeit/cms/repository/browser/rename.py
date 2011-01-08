# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import inspect
import z3c.flashmessage.interfaces
import zeit.cms.browser.lightbox
import zeit.cms.browser.menu
import zope.copypastemove.interfaces
import zope.formlib.form
import zope.interface
import zope.schema


class AlreadyExists(zope.schema.ValidationError):

    def doc(self):
        return self.args[0]


def valid_name(value):
    field = inspect.stack()[2][0].f_locals['self']
    context = field.context
    container = context.__parent__
    if value in container:
        raise AlreadyExists(
            _('"${name}" already exists.', mapping=dict(name=value)))
    return True


class IRenameSchema(zope.interface.Interface):

    new_name = zope.schema.TextLine(
        title=_('New file name'),
        constraint=valid_name)


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

        self.context = container[new_name]
        self.send_message(_('Renamed "${old_name}" to "${new_name}"',
                            mapping=dict(old_name=old_name,
                                         new_name=new_name)))


class MenuItem(zeit.cms.browser.menu.LightboxActionMenuItem):
    """Rename menu item."""

    title = _('Rename')

    def render(self):
        if zeit.cms.repository.interfaces.IRepositoryContent.providedBy(
            self.context):
            return super(MenuItem, self).render()
        return ''
