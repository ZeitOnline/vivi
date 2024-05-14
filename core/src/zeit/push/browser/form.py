import gocept.form.grouped
import zope.formlib.form

from zeit.cms.i18n import MessageFactory as _
from zeit.push.interfaces import ToggleDependentField
import zeit.cms.browser.form
import zeit.cms.testcontenttype.interfaces
import zeit.cms.testcontenttype.testcontenttype


class Base(zeit.cms.browser.form.CharlimitMixin):
    FormFieldsFactory = zope.formlib.form.FormFields

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        self._validate_dependency_constraints()

    def _validate_dependency_constraints(self):
        for widget in self.widgets:
            if isinstance(widget.context, ToggleDependentField):
                field_name = f'{self.prefix}.{widget.context.dependent_field}'
                if self.request.form.get(field_name):
                    self._set_widget_required(widget.context.getName())

    def _set_widget_required(self, name):
        field = self.widgets[name].context
        cloned = field.bind(field.context)
        cloned.required = True
        self.widgets[name].context = cloned


class SocialBase(Base):
    social_fields = gocept.form.grouped.Fields(
        _('Social media'),
        (
            'facebook_main_text',
            'short_text',
        ),
        css_class='wide-widgets column-left',
    )

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.form_fields += self.social_form_fields

    @property
    def social_form_fields(self):
        return self.FormFieldsFactory(zeit.push.interfaces.IAccountData).select(
            'facebook_main_text',
        ) + self.FormFieldsFactory(zeit.push.interfaces.IPushMessages).select('short_text')

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        self.set_charlimit('short_text')


class MobileBase(Base):
    mobile_fields = gocept.form.grouped.Fields(
        _('Mobile apps'),
        (
            'mobile_enabled',
            'mobile_payload_template',
            'mobile_title',
            'mobile_text',
            'mobile_uses_image',
            'mobile_image',
            'mobile_buttons',
        ),
        css_class='wide-widgets column-left',
    )

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.form_fields += self.mobile_form_fields

    @property
    def mobile_form_fields(self):
        return self.FormFieldsFactory(zeit.push.interfaces.IAccountData).select(
            'mobile_enabled',
            'mobile_payload_template',
            'mobile_title',
            'mobile_text',
            'mobile_uses_image',
            'mobile_image',
            'mobile_buttons',
        )

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        if hasattr(self.widgets['mobile_text'], 'extra'):
            # i.e. we're not in read-only mode
            self.widgets['mobile_text'].extra += ' cms:charwarning="40" cms:charlimit="150"'
            self.widgets['mobile_text'].cssClass = 'js-addbullet'


class SocialAddForm(SocialBase, MobileBase, zeit.cms.content.browser.form.CommonMetadataAddForm):
    form_fields = zope.formlib.form.FormFields(
        zeit.cms.testcontenttype.interfaces.IExampleContentType
    ).omit('authors', 'xml')
    factory = zeit.cms.testcontenttype.testcontenttype.ExampleContentType

    field_groups = zeit.cms.content.browser.form.CommonMetadataAddForm.field_groups + (
        SocialBase.social_fields,
        MobileBase.mobile_fields,
    )


class SocialEditForm(SocialBase, MobileBase, zeit.cms.browser.form.EditForm):
    form_fields = zope.formlib.form.FormFields()
