from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import zeit.cms.content.browser.form
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.cp.centerpage
import zeit.content.cp.interfaces
import zeit.content.image.interfaces
import zope.formlib.form
import zeit.seo.browser.form

base = zeit.cms.content.browser.form.CommonMetadataFormBase


class FormBase:

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.cms.interfaces.ICMSContent,
            zeit.cms.content.interfaces.ICommonMetadata).omit(
            'keywords') +
        zope.formlib.form.FormFields(
            zeit.content.image.interfaces.IImages) +
        zope.formlib.form.FormFields(
            zeit.content.cp.interfaces.ICenterPage).select(
            'type', 'header_image', 'topiclink_title',
            'topiclink_label_1', 'topiclink_url_1',
            'topiclink_label_2', 'topiclink_url_2',
            'topiclink_label_3', 'topiclink_url_3',
            'og_title', 'og_description', 'og_image',
            'keywords'))

    text_fields = gocept.form.grouped.Fields(
        _("Texts"),
        ('supertitle', 'byline', 'title', 'breadcrumb_title', 'subtitle',
         'teaserTitle', 'teaserText', 'image', 'fill_color', 'topiclink_title',
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


class EditForm(FormBase,
               zeit.cms.content.browser.form.CommonMetadataEditForm):

    title = _("Edit centerpage")


class DisplayForm(FormBase,
                  zeit.cms.content.browser.form.CommonMetadataDisplayForm):

    title = _("View centerpage metadata")


class SEOCpForm:
    form_fields = (
        zeit.seo.browser.form.SEOBaseForm.form_fields +
        zope.formlib.form.FormFields(
            zeit.content.cp.interfaces.ICpSEO).select(
                'enable_rss_tracking_parameter')
    )


class SEOView(SEOCpForm, zeit.seo.browser.form.SEODisplay):
    pass


class SEOEdit(SEOCpForm, zeit.seo.browser.form.SEOEdit):
    pass
