from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import zeit.cms.browser.form
import zeit.cms.testcontenttype.interfaces
import zeit.cms.testcontenttype.testcontenttype
import zope.formlib.form


class Base(zeit.cms.browser.form.CharlimitMixin):

    FormFieldsFactory = zope.formlib.form.FormFields

    def _set_widget_required(self, name):
        field = self.widgets[name].context
        cloned = field.bind(field.context)
        cloned.required = True
        self.widgets[name].context = cloned


class SocialBase(Base):

    social_fields = gocept.form.grouped.Fields(
        _("Social media"),
        ('facebook_main_text', 'facebook_main_enabled',
         'short_text', 'twitter_main_enabled',
         'twitter_ressort_enabled', 'twitter_ressort'),
        css_class='wide-widgets column-left')

    def __init__(self, *args, **kw):
        super(SocialBase, self).__init__(*args, **kw)
        self.form_fields += self.social_form_fields

    @property
    def social_form_fields(self):
        return (
            self.FormFieldsFactory(
                zeit.push.interfaces.IAccountData).select(
                    'facebook_main_text', 'facebook_main_enabled') +
            self.FormFieldsFactory(
                zeit.push.interfaces.IPushMessages).select('short_text') +
            self.FormFieldsFactory(
                zeit.push.interfaces.IAccountData).select(
                    'twitter_main_enabled',
                    'twitter_ressort_enabled', 'twitter_ressort'))

    def setUpWidgets(self, *args, **kw):
        super(SocialBase, self).setUpWidgets(*args, **kw)
        self.set_charlimit('short_text')
        if self.request.form.get('%s.facebook_main_enabled' % self.prefix):
            self._set_widget_required('facebook_main_text')
        if self.request.form.get('%s.twitter_ressort_enabled' % self.prefix):
            self._set_widget_required('twitter_ressort')


class MobileBase(Base):

    mobile_fields = gocept.form.grouped.Fields(
        _("Mobile apps"),
        ('mobile_title', 'mobile_text', 'mobile_enabled',
         'mobile_uses_image', 'mobile_image', 'mobile_buttons',
         'payload_template'),
        css_class='wide-widgets column-left')

    def __init__(self, *args, **kw):
        super(MobileBase, self).__init__(*args, **kw)
        self.form_fields += self.mobile_form_fields

    @property
    def mobile_form_fields(self):
        return self.FormFieldsFactory(
            zeit.push.interfaces.IAccountData).select(
                'mobile_enabled', 'mobile_title', 'mobile_text',
                'mobile_uses_image', 'mobile_image', 'mobile_buttons',
                'payload_template')

    def setUpWidgets(self, *args, **kw):
        super(MobileBase, self).setUpWidgets(*args, **kw)
        if self.request.form.get('%s.mobile_enabled' % self.prefix):
            self._set_widget_required('mobile_text')
        if self.request.form.get('%s.mobile_uses_image' % self.prefix):
            self._set_widget_required('mobile_image')
        if hasattr(self.widgets['mobile_text'], 'extra'):
            # i.e. we're not in read-only mode
            self.widgets['mobile_text'].extra += (
                ' cms:charwarning="40" cms:charlimit="150"')
            self.widgets['mobile_text'].cssClass = 'js-addbullet'


class SocialAddForm(
        SocialBase, MobileBase,
        zeit.cms.content.browser.form.CommonMetadataAddForm):

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.testcontenttype.interfaces.IExampleContentType).omit(
            'authors', 'xml')
    factory = zeit.cms.testcontenttype.testcontenttype.ExampleContentType

    field_groups = (
        zeit.cms.content.browser.form.CommonMetadataAddForm.field_groups +
        (SocialBase.social_fields, MobileBase.mobile_fields))


class SocialEditForm(SocialBase, MobileBase, zeit.cms.browser.form.EditForm):

    form_fields = zope.formlib.form.FormFields()
