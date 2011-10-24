# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.form.grouped
import zeit.cms.content.browser.form
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.cp.centerpage
import zope.formlib.form
from zeit.content.cp.i18n import MessageFactory as _

base = zeit.cms.content.browser.form.CommonMetadataFormBase

class FormBase(object):

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.cms.interfaces.ICMSContent,
            zeit.cms.content.interfaces.ICommonMetadata)
        + zope.formlib.form.FormFields(
            zeit.content.cp.interfaces.ICenterPage).select(
            'type', 'header_image', 'snapshot', 'topiclink_title', 
            'topiclink_label_1', 'topiclink_url_1',
            'topiclink_label_2', 'topiclink_url_2',
            'topiclink_label_3', 'topiclink_url_3',
            'topiclink_label_4', 'topiclink_url_4',))

    text_fields = gocept.form.grouped.Fields(
        _("Texts"),
        ('supertitle', 'byline', 'title', 'subtitle',
         'teaserTitle', 'teaserText', 'topiclink_title',
         'topiclink_label_1', 'topiclink_url_1',
         'topiclink_label_2', 'topiclink_url_2',
         'topiclink_label_3', 'topiclink_url_3',
         'topiclink_label_4', 'topiclink_url_4',
        ),
        css_class='wide-widgets column-left')

    field_groups = (
        base.navigation_fields,
        base.head_fields,
        text_fields,
        gocept.form.grouped.RemainingFields(
            _("misc."),
            css_class='column-right'),
        base.option_fields,
        )


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
