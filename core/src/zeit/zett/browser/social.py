# XXX 100% copy&paste from zeit.magazin.browser.social
import copy
import zeit.push.browser.form
import zeit.push.interfaces


class SocialBase(zeit.push.browser.form.SocialBase):

    zett_fields = ('facebook_zett_text', 'facebook_zett_enabled')

    social_fields = copy.copy(zeit.push.browser.form.SocialBase.social_fields)
    social_fields.fields = (
        social_fields.fields[:2] +
        zett_fields +
        social_fields.fields[2:]
    )

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        # Insert zett_fields at the wanted position
        self.form_fields = self.form_fields.omit(*self.social_fields.fields)
        self.form_fields += self.social_form_fields.select(
            *self.social_fields.fields)

    @property
    def social_form_fields(self):
        form_fields = super().social_form_fields
        return (
            form_fields +
            self.FormFieldsFactory(zeit.push.interfaces.IAccountData).select(
                *self.zett_fields))
