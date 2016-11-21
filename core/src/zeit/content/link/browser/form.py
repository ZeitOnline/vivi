from zeit.cms.i18n import MessageFactory as _
import copy
import zeit.cms.content.browser.form
import zeit.content.link.interfaces
import zeit.content.link.link
import zeit.push.browser.form
import zope.formlib.form


base = zeit.cms.content.browser.form.CommonMetadataFormBase


class Base(zeit.push.browser.form.SocialBase):

    # XXX We should switch to explicit select.
    form_fields = zope.formlib.form.FormFields(
        zeit.content.link.interfaces.ILink).omit(
            'xml', 'authors', 'push_news', 'deeplink_url', 'blog',
            'bigshare_buttons')

    social_fields = copy.copy(zeit.push.browser.form.SocialBase.social_fields)
    social_fields_list = list(social_fields.fields)
    social_fields_list.remove('bigshare_buttons')
    social_fields.fields = tuple(social_fields_list)

    field_groups = (
        base.field_groups[:4] +
        (social_fields,
         base.option_fields,
         base.author_fields)
    )

    @property
    def social_form_fields(self):
        return super(Base, self).social_form_fields.omit('bigshare_buttons')


class Add(Base, zeit.cms.content.browser.form.CommonMetadataAddForm):

    title = _('Add link')
    factory = zeit.content.link.link.Link

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
