from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.form
import zeit.content.text.interfaces
import zeit.content.text.text
import zope.app.form.browser.textwidgets
import zope.formlib.form


class FormBase(object):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.text.interfaces.IText)


class Add(FormBase, zeit.cms.browser.form.AddForm):

    title = _('Add plain text')
    factory = zeit.content.text.text.Text


class Edit(FormBase, zeit.cms.browser.form.EditForm):

    title = _('Edit plain text')


class Display(FormBase, zeit.cms.browser.form.DisplayForm):

    title = _('View plain text')
