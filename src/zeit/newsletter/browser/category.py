# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import zeit.cms.browser.form
import zeit.cms.browser.view
import zeit.newsletter.interfaces
import zope.formlib.form


class AddAndCheckout(zeit.cms.browser.view.Base):

    def __call__(self):
        newsletter = self.context.create()
        self.redirect(self.url(newsletter, '@@checkout'))


class FormBase(object):

    form_fields = zope.formlib.form.FormFields(
        zeit.newsletter.interfaces.INewsletterCategory)

    field_groups = (
        gocept.form.grouped.Fields(_('Middle ad'), (
            'ad_middle_title', 'ad_middle_text', 'ad_middle_href',
            'ad_middle_image', 'ad_middle_groups_above'
        )),
        gocept.form.grouped.Fields(_('Bottom ad'), (
            'ad_bottom_title', 'ad_bottom_text', 'ad_bottom_href',
            'ad_bottom_image',
        )),
        gocept.form.grouped.Fields(_('General'), (
            'subject', 'ressorts', 'video_playlist',
        )),
        gocept.form.grouped.Fields(_('Optivo'), (
            'mandant', 'recipientlist', 'recipientlist_test',
        )),
    )


class DisplayForm(FormBase, zeit.cms.browser.form.DisplayForm):

    title = _('Newsletter metadata')


class EditForm(FormBase, zeit.cms.browser.form.EditForm):

    title = _('Edit metadata')
    form_fields = FormBase.form_fields.omit('__name__', 'last_created')
