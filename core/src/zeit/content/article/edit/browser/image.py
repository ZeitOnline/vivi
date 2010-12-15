# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.interfaces
import zeit.content.article.edit.interfaces
import zeit.edit.browser.view
import zope.lifecycleevent


class EditImage(zeit.edit.browser.view.EditBox):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.IImage).omit('references')


class EditImageAction(zeit.edit.browser.view.EditBoxAction):

    title = _('Edit')
    action = 'edit-layout'
