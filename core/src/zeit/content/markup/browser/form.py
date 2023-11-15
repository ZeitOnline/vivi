from zeit.cms.i18n import MessageFactory as _

import gocept.form.grouped
import zope.formlib.form

import zeit.cms.browser.form
import zeit.cms.browser.widget
import zeit.content.markup.interfaces
import zeit.content.markup.markup


class Base:
    form_fields = zope.formlib.form.FormFields(zeit.content.markup.interfaces.IMarkup).select(
        'title', 'text', 'authorships'
    )

    field_groups = (
        gocept.form.grouped.Fields(_('Markup Content'), ('title', 'authorships', 'text')),
    )


class Add(Base, zeit.cms.browser.form.AddForm):
    title = _('Add markup')
    factory = zeit.content.markup.markup.Markup
    form_fields = Base.form_fields + zope.formlib.form.FormFields(
        zeit.content.markup.interfaces.IMarkup
    ).select('__name__')

    field_groups = (
        gocept.form.grouped.Fields(_('Navigation'), ('__name__',), css_class='column-right'),
    ) + Base.field_groups


class Edit(Base, zeit.cms.browser.form.EditForm):
    title = _('Edit markup')


class Display(Base, zeit.cms.browser.form.DisplayForm):
    title = _('Display markup metadata')
