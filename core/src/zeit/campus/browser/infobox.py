import zope.formlib.form

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.form
import zeit.content.infobox.browser.form
import zeit.content.infobox.infobox
import zeit.content.infobox.interfaces


# XXX copy&paste of zeit.content.infobox.browser.form to add
# IDebate to all form_fields


class FormBase(zeit.content.infobox.browser.form.FormBase):
    form_fields = (
        zeit.content.infobox.browser.form.FormBase.form_fields
        + zope.formlib.form.FormFields(zeit.content.infobox.interfaces.IDebate)
    )


class Add(FormBase, zeit.cms.browser.form.AddForm):
    factory = zeit.content.infobox.infobox.Infobox
    title = _('Add infobox')


class Edit(FormBase, zeit.cms.browser.form.EditForm):
    title = _('Edit infobox')
    form_fields = FormBase.form_fields.omit('__name__')


class Display(FormBase, zeit.cms.browser.form.DisplayForm):
    title = _('View infobox')
    form_fields = FormBase.form_fields.omit('__name__')
    for_display = True
