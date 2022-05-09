import copy
import zeit.push.browser.form
import zeit.push.interfaces


class SocialBase(zeit.push.browser.form.SocialBase):

    magazin_fields = ('facebook_magazin_text', 'facebook_magazin_enabled')

    social_fields = copy.copy(zeit.push.browser.form.SocialBase.social_fields)
    social_fields.fields = (
        social_fields.fields[:2] +
        magazin_fields +
        social_fields.fields[2:]
    )

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        # Insert magazin_fields at the wanted position
        self.form_fields = self.form_fields.omit(*self.social_fields.fields)
        self.form_fields += self.social_form_fields.select(
            *self.social_fields.fields)

    @property
    def social_form_fields(self):
        return (
            super().social_form_fields +
            self.FormFieldsFactory(zeit.push.interfaces.IAccountData).select(
                *self.magazin_fields))

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        if self.request.form.get('%s.facebook_magazin_enabled' % self.prefix):
            self._set_widget_required('facebook_magazin_text')
