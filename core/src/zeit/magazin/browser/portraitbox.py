import gocept.form.grouped
import zope.formlib.form

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.form
import zeit.content.portraitbox.interfaces
import zeit.content.portraitbox.portraitbox
import zeit.magazin.interfaces
import zeit.wysiwyg.interfaces


# XXX complete copy&paste of zeit.content.portraitbox.browser.form to add
# IPortraitboxLongtext to all form_fields


class FormBase:
    form_fields = zope.formlib.form.FormFields(
        zeit.content.portraitbox.interfaces.IPortraitbox,
        zeit.wysiwyg.interfaces.IHTMLContent,
        zeit.magazin.interfaces.IPortraitboxLongtext,
    ).omit('text', 'xml')

    field_groups = (
        gocept.form.grouped.RemainingFields(_('Head'), css_class='column-right'),
        gocept.form.grouped.Fields(
            _('Portrait'),
            ('name', 'html', 'longtext', 'image'),
            css_class='full-width wide-widgets',
        ),
    )


class Add(FormBase, zeit.cms.browser.form.AddForm):
    factory = zeit.content.portraitbox.portraitbox.Portraitbox
    title = _('Add portraitbox')


class Edit(FormBase, zeit.cms.browser.form.EditForm):
    title = _('Edit portraitbox')
    form_fields = FormBase.form_fields.omit('__name__')


class Display(FormBase, zeit.cms.browser.form.DisplayForm):
    title = _('View portraitbox')
    form_fields = FormBase.form_fields.omit('__name__')
