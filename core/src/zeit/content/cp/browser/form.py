# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.i18n import MessageFactory as _
import gocept.form.grouped
import grokcore.component as grok
import zeit.cms.content.browser.form
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.cp.centerpage
import zope.formlib.form

base = zeit.cms.content.browser.form.CommonMetadataFormBase


class FormBase(object):

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.cms.interfaces.ICMSContent,
            zeit.cms.content.interfaces.ICommonMetadata).omit('keywords')
        + zope.formlib.form.FormFields(
            zeit.content.cp.interfaces.ICenterPage).select(
            'type', 'header_image', 'snapshot', 'topiclink_title',
            'topiclink_label_1', 'topiclink_url_1',
            'topiclink_label_2', 'topiclink_url_2',
            'topiclink_label_3', 'topiclink_url_3',
            'og_title', 'og_description', 'og_image',
            'keywords'))

    text_fields = gocept.form.grouped.Fields(
        _("Texts"),
        ('supertitle', 'byline', 'title', 'breadcrumb_title', 'subtitle',
         'teaserTitle', 'teaserText', 'topiclink_title',
         'topiclink_label_1', 'topiclink_url_1',
         'topiclink_label_2', 'topiclink_url_2',
         'topiclink_label_3', 'topiclink_url_3',
         ),
        css_class='wide-widgets column-left')

    og_fields = gocept.form.grouped.Fields(
        _("OG Metadata"),
         ('og_title', 'og_description', 'og_image'),
        css_class='wide-widgets column-right')

    field_groups = (
        base.navigation_fields,
        base.head_fields,
        text_fields,
        gocept.form.grouped.RemainingFields(
            _("misc."),
            css_class='column-right'),
        base.option_fields,
        og_fields,
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
    form_fields = FormBase.form_fields + zope.formlib.form.FormFields(
        zeit.content.cp.interfaces.IAutomaticRegion).select(
            'count', 'raw_query', 'automatic')

    automatic_fields = gocept.form.grouped.Fields(
        _("Automatic contents"),
         ('automatic', 'count', 'raw_query'))
    field_groups = (automatic_fields,) + FormBase.field_groups


class DisplayForm(FormBase,
                  zeit.cms.content.browser.form.CommonMetadataDisplayForm):

    title = _("View centerpage metadata")


@grok.adapter(zeit.content.cp.interfaces.ICenterPage)
@grok.implementer(zeit.content.cp.interfaces.IAutomaticRegion)
def autoregion_for_cp(context):
    return zeit.content.cp.interfaces.IAutomaticRegion(context['lead'])
