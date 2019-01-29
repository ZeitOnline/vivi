from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.form
import zeit.content.text.embed
import zeit.content.text.interfaces
import zope.formlib.form


class FormBase(object):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.text.interfaces.IEmbed)


class Add(FormBase, zeit.cms.browser.form.AddForm):

    title = _('Add embed')
    factory = zeit.content.text.embed.Embed


class Edit(FormBase, zeit.cms.browser.form.EditForm):

    title = _('Edit embed')


class Display(FormBase, zeit.cms.browser.form.DisplayForm):

    title = _('View embed')
