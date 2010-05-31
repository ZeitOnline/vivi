# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.form
import zeit.content.author.author
import zeit.content.author.interfaces
import zope.formlib.form


class FormBase(object):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.author.interfaces.IAuthor,
        zeit.cms.interfaces.ICMSContent)


class AddForm(FormBase,
              zeit.cms.browser.form.AddForm):

    title = _('Add author')
    factory = zeit.content.author.author.Author


class EditForm(FormBase,
               zeit.cms.browser.form.EditForm):

    title = _('Edit author')


class DisplayForm(FormBase,
                  zeit.cms.browser.form.DisplayForm):

    title = _('View')
