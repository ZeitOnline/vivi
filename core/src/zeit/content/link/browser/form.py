
from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.browser.form
import zeit.content.link.interfaces
import zeit.content.link.link
import zeit.push.browser.form
import zope.app.appsetup.appsetup
import zope.formlib.form


base = zeit.cms.content.browser.form.CommonMetadataFormBase


class Base(zeit.push.browser.form.SocialBase):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.link.interfaces.ILink).omit(
            'xml', 'authors', 'push_news', 'deeplink_url', 'blog')

    field_groups = (
        base.field_groups[:4]
        + (base.option_fields,
           base.author_fields)
    )

    def __init__(self, *args, **kw):
        super(Base, self).__init__(*args, **kw)
        if zope.app.appsetup.appsetup.getConfigContext().hasFeature(
                'zeit.push.social-form'):
            self.field_groups = (
                self.field_groups[:4]
                + (zeit.push.browser.form.SocialBase.social_fields,)
                + self.field_groups[4:]
            )


class Add(Base, zeit.cms.content.browser.form.CommonMetadataAddForm):

    title = _('Add link')
    factory = zeit.content.link.link.Link
    form_fields = Base.form_fields.omit(
        'automaticMetadataUpdateDisabled')

    def applyChanges(self, object, data):
        self.applyAccountData(object, data)
        return super(Add, self).applyChanges(object, data)


class Edit(Base,
           zeit.cms.content.browser.form.CommonMetadataEditForm):

    title = _('Edit link')

    @zope.formlib.form.action(
        _('Apply'), condition=zope.formlib.form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        self.applyAccountData(self.context, data)
        super(Edit, self).handle_edit_action.success(data)


class Display(Base, zeit.cms.content.browser.form.CommonMetadataDisplayForm):

    title = _('View link metadata')
