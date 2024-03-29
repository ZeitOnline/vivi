import zope.component
import zope.formlib.form

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.form
import zeit.cms.repository.folder


class FolderAdd(zeit.cms.browser.form.AddForm):
    form_fields = zope.formlib.form.Fields(zeit.cms.repository.interfaces.IFolder).omit('uniqueId')
    title = _('Add folder')
    widget_groups = ((_('Folder'), zeit.cms.browser.form.REMAINING_FIELDS, ''),)

    factory = zeit.cms.repository.folder.Folder
    checkout = False


class FolderEdit:
    title = _('Edit folder')

    def __call__(self):
        url = zope.component.getMultiAdapter((self.context, self.request), name='absolute_url')()
        self.request.response.redirect(url)
        return ''
