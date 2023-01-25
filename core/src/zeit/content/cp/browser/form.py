from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import itertools
import zeit.cms.content.browser.form
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.cp.centerpage
import zeit.content.cp.interfaces
import zeit.content.image.interfaces
import zope.formlib.form
import zeit.seo.browser.form


class FormBase:

    text_fields = gocept.form.grouped.Fields(
        _("Texts"),
        ('supertitle', 'byline', 'title', 'subtitle',
         'teaserTitle', 'teaserText', 'image', 'fill_color', 'topiclink_title',
         'topiclink_label_1', 'topiclink_url_1',
         'topiclink_label_2', 'topiclink_url_2',
         'topiclink_label_3', 'topiclink_url_3',
         'topiclink_label_4', 'topiclink_url_4',
         'topiclink_label_5', 'topiclink_url_5',
         'liveblog_label_1', 'liveblog_url_1',
         'liveblog_label_2', 'liveblog_url_2',
         'liveblog_label_3', 'liveblog_url_3',
         ),
        css_class='wide-widgets column-left')

    og_fields = gocept.form.grouped.Fields(
        _("OG Metadata"),
         ('og_title', 'og_description', 'og_image'),
        css_class='wide-widgets column-right')

    head_fields = gocept.form.grouped.Fields(
        _("Head"),
        ('ressort', 'sub_ressort'),
        css_class='widgets-float column-left')

    option_fields = gocept.form.grouped.Fields(
        _("Options"),
        ('type',
         'banner_id', 'cap_title', 'advertisement_title', 'advertisement_text',
         'overscrolling'),
        css_class='column-right checkboxes')

    auto_cp_fields = gocept.form.grouped.Fields(
        _("Run in channel"),
        ('channels',),
        css_class='column-right')

    navigation_fields = gocept.form.grouped.Fields(
        _("Navigation"),
        ('__name__', 'keywords', 'serie', 'product', 'copyrights'),
        css_class='column-right')

    cpform_fields = zope.formlib.form.FormFields(
        zeit.content.cp.interfaces.ICenterPage,
        zeit.content.image.interfaces.IImages)

    form_fields = cpform_fields.select(*list(itertools.chain.from_iterable(
        [group.get_field_names() for group in (
            text_fields,
            og_fields,
            head_fields,
            option_fields,
            auto_cp_fields,
            navigation_fields,
        )])))

    field_groups = (
        text_fields,
        navigation_fields,
        auto_cp_fields,
        og_fields,
        option_fields,
        head_fields,
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
        # ICenterPage statically provides ISkipEnrich,
        # so there's no point in adding it to individual objects.
    ).omit('disable_enrich')


class SEOView(SEOCpForm, zeit.seo.browser.form.SEODisplay):
    pass


class SEOEdit(SEOCpForm, zeit.seo.browser.form.SEOEdit):
    pass
