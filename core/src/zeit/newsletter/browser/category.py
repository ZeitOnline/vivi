# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
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


class DisplayForm(FormBase, zeit.cms.browser.form.DisplayForm):

    title = _('Newsletter metadata')


class EditForm(FormBase, zeit.cms.browser.form.EditForm):

    title = _('Edit metadata')
    form_fields = FormBase.form_fields.omit('__name__', 'last_created')
