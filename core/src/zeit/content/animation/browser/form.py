from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import zeit.cms.browser.form
import zeit.content.animation.interfaces
import zeit.content.image.interfaces
import zeit.push.browser.form
import zope.formlib.form


class Base:

    form_fields = zope.formlib.form.FormFields(
        zeit.content.animation.interfaces.IAnimation
    ).select("article", "video", "images", "display_mode")

    field_groups = (
        gocept.form.grouped.RemainingFields(_("Article")),
        gocept.form.grouped.Fields(
            _("Teaser"), ("display_mode", "images", "video")),
    )


class Add(Base, zeit.cms.browser.form.AddForm):

    title = _("Add animated teaser")
    factory = zeit.content.animation.animation.Animation
    form_fields = Base.form_fields + zope.formlib.form.FormFields(
        zeit.content.animation.interfaces.IAnimation
    ).select("__name__")

    field_groups = (
        gocept.form.grouped.Fields(
            _("Navigation"), ("__name__",), css_class="column-right"
        ),
    ) + Base.field_groups


class Edit(Base, zeit.cms.browser.form.EditForm):
    pass


class Display(Base, zeit.cms.browser.form.DisplayForm):
    pass
