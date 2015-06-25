from zeit.cms.asset.browser.form import AssetBase  # Legacy
from zeit.cms.i18n import MessageFactory as _
import copy
import gocept.form.grouped
import zeit.cms.browser.form
import zeit.cms.content.interfaces
import zeit.cms.settings.interfaces
import zope.app.appsetup.appsetup
import zope.app.form.browser.textwidgets


class ShowLimitInputWidget(zope.app.form.browser.textwidgets.TextAreaWidget):

    def __call__(self):
        max_length = self.context.max_length
        result = [
            '<div class="show-input-limit" maxlength="%s"></div>' % max_length,
            super(ShowLimitInputWidget, self).__call__(),
            ('<script type="text/javascript">new zeit.cms.InputValidation('
             '"%s");</script>') % self.name]

        return ''.join(result)


class CommonMetadataFormBase(object):

    navigation_fields = gocept.form.grouped.Fields(
        _("Navigation"),
        ('__name__', 'keywords', 'serie', 'product', 'copyrights'),
        css_class='column-right')
    head_fields = gocept.form.grouped.Fields(
        _("Head"),
        ('year', 'volume', 'page', 'ressort', 'sub_ressort'),
        css_class='widgets-float column-left')
    text_fields = gocept.form.grouped.Fields(
        _("Texts"),
        ('supertitle', 'byline', 'title', 'breadcrumb_title', 'subtitle',
         'teaserTitle', 'teaserText', 'teaserSupertitle'),
        css_class='wide-widgets column-left')
    option_fields = gocept.form.grouped.Fields(
        _("Options"),
        ('dailyNewsletter', 'commentsAllowed', 'commentSectionEnable',
         'foldable',
         'minimal_header', 'countings', 'is_content', 'in_rankings',
         'banner', 'banner_id', 'breaking_news', 'mobile_alternative',
         'rebrush_website_content'),
        css_class='column-right checkboxes')
    author_fields = gocept.form.grouped.Fields(
        _("Authors"),
        ('authorships', 'authors'),
        css_class='wide-widgets column-left')
    auto_cp_fields = gocept.form.grouped.Fields(
        _("Run in channel"),
        ('channels', 'lead_candidate'),
        css_class='column-right')

    field_groups = (
        navigation_fields,
        head_fields,
        text_fields,
        gocept.form.grouped.RemainingFields(
            _("misc."),
            css_class='column-right'),
        auto_cp_fields,
        author_fields,
        option_fields,
    )
    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata).omit('push_news')

    for_display = False

    def __init__(self, context, request):
        super(CommonMetadataFormBase, self).__init__(context, request)
        if not self.for_display:
            # Change the widgets of the teaser fields
            change_field_names = ('teaserText',)
            form_fields = self.form_fields.omit(*change_field_names)
            changed_fields = []
            for field in change_field_names:
                field = copy.copy(self.form_fields[field])
                field.custom_widget = ShowLimitInputWidget
                changed_fields.append(field)
            self.form_fields = form_fields + zope.formlib.form.FormFields(
                *changed_fields)


class CommonMetadataAddForm(CommonMetadataFormBase,
                            zeit.cms.browser.form.AddForm):
    """Add form which contains the common metadata."""

    def setUpWidgets(self, ignore_request=False):
        if not ignore_request:
            if 'form.actions.add' not in self.request:
                settings = zeit.cms.settings.interfaces.IGlobalSettings(
                    self.context)
                form = self.request.form
                form['form.year'] = str(settings.default_year)
                form['form.volume'] = str(settings.default_volume)
        super(CommonMetadataAddForm, self).setUpWidgets(ignore_request)


class CommonMetadataEditForm(CommonMetadataFormBase,
                             zeit.cms.browser.form.EditForm):
    """Edit form which contains the common metadata."""


class CommonMetadataDisplayForm(CommonMetadataFormBase,
                                zeit.cms.browser.form.DisplayForm):
    """Display form which contains the common metadata."""

    for_display = True  # omit custom widget w/ js-validation
