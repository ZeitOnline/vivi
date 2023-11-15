import copy
import zeit.content.link.browser.form
import zeit.magazin.browser.social


base = zeit.content.link.browser.form.Base
social_fields = copy.copy(zeit.push.browser.form.SocialBase.social_fields)
field_groups = base.link_field_groups + (social_fields,)


class Add(zeit.magazin.browser.social.SocialBase, zeit.content.link.browser.form.Add):
    field_groups = field_groups
    social_fields = social_fields


class Edit(zeit.magazin.browser.social.SocialBase, zeit.content.link.browser.form.Edit):
    field_groups = field_groups
    social_fields = social_fields


class Display(zeit.magazin.browser.social.SocialBase, zeit.content.link.browser.form.Display):
    field_groups = field_groups
    social_fields = social_fields
