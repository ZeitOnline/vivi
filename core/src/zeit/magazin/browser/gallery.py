import zeit.content.gallery.browser.form
import zeit.magazin.browser.social


base = zeit.content.gallery.browser.form.GalleryFormBase
field_groups = (
    base.field_groups[:4]
    + (zeit.magazin.browser.social.SocialBase.social_fields,)
    + base.field_groups[5:]
)


class Add(zeit.magazin.browser.social.SocialBase, zeit.content.gallery.browser.form.AddGallery):
    field_groups = field_groups


class Edit(zeit.magazin.browser.social.SocialBase, zeit.content.gallery.browser.form.EditGallery):
    field_groups = field_groups


class Display(
    zeit.magazin.browser.social.SocialBase, zeit.content.gallery.browser.form.DisplayGallery
):
    field_groups = field_groups
