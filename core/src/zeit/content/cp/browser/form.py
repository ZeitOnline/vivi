# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.content.browser.form
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.cp.centerpage
import zope.formlib.form
from zeit.content.cp.i18n import MessageFactory as _


class FormBase(object):

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.cms.interfaces.ICMSContent,
            zeit.cms.content.interfaces.ICommonMetadata)
        + zope.formlib.form.FormFields(
            zeit.content.cp.interfaces.ICenterPage).select('type'))


class AddForm(FormBase,
              zeit.cms.content.browser.form.CommonMetadataAddForm):

    title = _("Add centerpage")
    factory = zeit.content.cp.centerpage.CenterPage
    next_view = 'view.html'
    form_fields = FormBase.form_fields.omit(
        'automaticMetadataUpdateDisabled')


class EditForm(FormBase,
               zeit.cms.content.browser.form.CommonMetadataEditForm):

    title = _("Edit centerpage")


class DisplayForm(FormBase,
                  zeit.cms.content.browser.form.CommonMetadataDisplayForm):

    title = _("View centerpage metadata")
