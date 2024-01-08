# XXX 100% copy&paste from zeit.magazin.browser.social
import zeit.campus.browser.social
import zeit.content.gallery.browser.form


base = zeit.content.gallery.browser.form.GalleryFormBase
field_groups = (
    base.field_groups[:4]
    + (zeit.campus.browser.social.SocialBase.social_fields,)
    + base.field_groups[5:]
)


class Add(zeit.campus.browser.social.SocialBase, zeit.content.gallery.browser.form.AddGallery):
    field_groups = field_groups


class Edit(zeit.campus.browser.social.SocialBase, zeit.content.gallery.browser.form.EditGallery):
    field_groups = field_groups


class Display(
    zeit.campus.browser.social.SocialBase, zeit.content.gallery.browser.form.DisplayGallery
):
    field_groups = field_groups
