import gocept.form.grouped
import zope.formlib.form

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.form
import zeit.content.advertisement.advertisement
import zeit.content.advertisement.interfaces


class Base:
    form_fields = zope.formlib.form.FormFields(
        zeit.content.advertisement.interfaces.IAdvertisement
    ).select('title', 'text', 'button_text', 'button_color', 'image', 'supertitle', 'url')

    field_groups = (gocept.form.grouped.RemainingFields(_('Texts')),)


class Add(Base, zeit.cms.browser.form.AddForm):
    title = _('Add publisher advertisement')
    factory = zeit.content.advertisement.advertisement.Advertisement
    form_fields = Base.form_fields + zope.formlib.form.FormFields(
        zeit.content.advertisement.interfaces.IAdvertisement
    ).select('__name__')

    field_groups = (
        gocept.form.grouped.Fields(_('Navigation'), ('__name__',), css_class='column-right'),
    ) + Base.field_groups


class Edit(Base, zeit.cms.browser.form.EditForm):
    pass


class Display(Base, zeit.cms.browser.form.DisplayForm):
    pass
