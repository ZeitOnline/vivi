from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.form
import zeit.content.dynamicfolder.interfaces
import zope.formlib.form


class FormBase(object):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.dynamicfolder.interfaces.IDynamicFolder)


class DisplayForm(FormBase, zeit.cms.browser.form.DisplayForm):
    pass


class EditForm(FormBase, zeit.cms.browser.form.EditForm):

    title = _('Edit metadata')
    form_fields = FormBase.form_fields.omit('__name__')
