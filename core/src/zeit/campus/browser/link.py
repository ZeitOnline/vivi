# XXX 100% copy&paste from zeit.magazin.browser.social
import zeit.content.link.browser.form
import zeit.campus.browser.social


base = zeit.content.link.browser.form.Base
field_groups = (
    base.field_groups[:4]
    + (zeit.campus.browser.social.SocialBase.social_fields,)
    + base.field_groups[5:]
)


class Add(zeit.campus.browser.social.SocialBase,
          zeit.content.link.browser.form.Add):

    field_groups = field_groups


class Edit(zeit.campus.browser.social.SocialBase,
           zeit.content.link.browser.form.Edit):

    field_groups = field_groups


class Display(zeit.campus.browser.social.SocialBase,
              zeit.content.link.browser.form.Display):

    field_groups = field_groups
