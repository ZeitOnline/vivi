# XXX 100% copy&paste from zeit.magazin.browser.social
import copy
import zeit.push.browser.form
import zeit.push.interfaces


class SocialBase(zeit.push.browser.form.SocialBase):

    campus_fields = ('facebook_campus_text', 'facebook_campus_enabled')

    social_fields = copy.copy(zeit.push.browser.form.SocialBase.social_fields)
    social_fields_list = list(social_fields.fields)
    social_fields_list.remove('bigshare_buttons')
    social_fields.fields = tuple(social_fields_list)
    social_fields.fields = (
        social_fields.fields[:2] +
        campus_fields +
        social_fields.fields[2:]
    )

    def __init__(self, *args, **kw):
        super(SocialBase, self).__init__(*args, **kw)
        # Insert campus_fields at the wanted position
        self.form_fields = self.form_fields.omit(*self.social_fields.fields)
        self.form_fields += self.social_form_fields.select(
            *self.social_fields.fields)

    @property
    def social_form_fields(self):
        form_fields = super(SocialBase, self).social_form_fields
        form_fields = form_fields.omit('bigshare_buttons')
        return (
            form_fields +
            self.FormFieldsFactory(zeit.push.interfaces.IAccountData).select(
                *self.campus_fields))

    def setUpWidgets(self, *args, **kw):
        super(SocialBase, self).setUpWidgets(*args, **kw)
        if self.request.form.get('%s.facebook_campus_enabled' % self.prefix):
            self._set_widget_required('facebook_campus_text')
