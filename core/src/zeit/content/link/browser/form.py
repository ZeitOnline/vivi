# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt
"""Link forms."""

from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import zeit.cms.content.browser.form
import zeit.content.link.interfaces
import zeit.content.link.link
import zeit.push.browser.form
import zope.formlib.form


class Base(object):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.link.interfaces.ILink).omit(
            'xml', 'authors')


class Add(Base, zeit.cms.content.browser.form.CommonMetadataAddForm):

    title = _('Add link')
    factory = zeit.content.link.link.Link
    form_fields = Base.form_fields.omit(
        'automaticMetadataUpdateDisabled')


class Edit(Base,
           zeit.push.browser.form.SocialBase,
           zeit.cms.content.browser.form.CommonMetadataEditForm):

    title = _('Edit link')

    def __init__(self, *args, **kw):
        social_fields = gocept.form.grouped.Fields(
            _("Social media"),
            ('long_text', 'facebook', 'facebook_magazin',
             'short_text', 'twitter', 'twitter_ressort'),
            css_class='wide-widgets column-left')
        if zope.app.appsetup.appsetup.getConfigContext().hasFeature(
                'zeit.content.article.social-push-mobile'):
            social_fields.fields += ('mobile',)
        social_fields.fields += ('enabled',)
        self.field_groups = self.field_groups[:3] + (
            social_fields,) + self.field_groups[3:]
        super(Edit, self).__init__(*args, **kw)

    @zope.formlib.form.action(
        _('Apply'), condition=zope.formlib.form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        self.applyAccountData(data)
        return super(Edit, self).handle_edit_action.success(data)


class Display(Base, zeit.cms.content.browser.form.CommonMetadataDisplayForm):

    title = _('View link metadata')
