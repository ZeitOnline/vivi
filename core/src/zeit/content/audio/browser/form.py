from zeit.cms.i18n import MessageFactory as _
import zope.formlib
import gocept.form.grouped
import zeit.cms.browser.form
import zeit.content.audio.interfaces
import zeit.content.audio.audio


class Base:

    form_fields = zope.formlib.form.FormFields(
        zeit.content.audio.interfaces.IAudio).select(
            'title', 'episode_id', 'url')

    field_groups = (
        gocept.form.grouped.RemainingFields(
            _('Texts')),
    )


class Add(Base, zeit.cms.browser.form.AddForm):

    title = _('Add audio')
    factory = zeit.content.audio.audio.Audio
    form_fields = Base.form_fields + zope.formlib.form.FormFields(
        zeit.content.audio.interfaces.IAudio).select(
            '__name__')

    field_groups = (
        (gocept.form.grouped.Fields(
            _('Navigation'), ('__name__',), css_class='column-right'),)
        + Base.field_groups)


class Edit(Base, zeit.cms.browser.form.EditForm):
    pass


class Display(Base, zeit.cms.browser.form.DisplayForm):
    pass
