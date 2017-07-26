from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.browser.form
import zeit.content.link.interfaces
import zeit.content.link.link
import zeit.push.browser.form
import zope.formlib.form


base = zeit.cms.content.browser.form.CommonMetadataFormBase


class Base(zeit.push.browser.form.SocialBase,
           zeit.push.browser.form.MobileBase):

    # XXX We should switch to explicit select.
    form_fields = zope.formlib.form.FormFields(
        zeit.content.link.interfaces.ILink).omit(
            'xml', 'authors', 'deeplink_url', 'blog')

    field_groups = (
        base.field_groups[:4] +
        (zeit.push.browser.form.SocialBase.social_fields,
         zeit.push.browser.form.MobileBase.mobile_fields,
         base.option_fields,
         base.author_fields)
    )


class Add(Base, zeit.cms.content.browser.form.CommonMetadataAddForm):

    title = _('Add link')
    factory = zeit.content.link.link.Link


class Edit(Base,
           zeit.cms.content.browser.form.CommonMetadataEditForm):

    title = _('Edit link')


class Display(Base, zeit.cms.content.browser.form.CommonMetadataDisplayForm):

    title = _('View link metadata')
