# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt
"""Content related forms."""

from zeit.cms.asset.browser.form import AssetBase  # Legacy
from zeit.cms.i18n import MessageFactory as _
import copy
import gocept.form.grouped
import zc.resourcelibrary
import zeit.cms.browser.form
import zeit.cms.browser.interfaces
import zeit.cms.content.browser.interfaces
import zeit.cms.content.interfaces
import zeit.cms.related.interfaces
import zeit.cms.settings.interfaces
import zope.app.appsetup.interfaces
import zope.app.form.browser.textwidgets
import zope.testing.cleanup


class ShowLimitInputWidget(zope.app.form.browser.textwidgets.TextAreaWidget):

    def __call__(self):
        zc.resourcelibrary.need('zeit.cms.content.validation')
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
        ('supertitle', 'byline', 'title', 'subtitle',
         'teaserTitle', 'teaserText', 'teaserSupertitle'),
        css_class='wide-widgets column-left')
    option_fields = gocept.form.grouped.Fields(
        _("Options"),
        ('dailyNewsletter', 'commentsAllowed', 'commentSectionEnable', 'foldable',
         'minimal_header', 'countings', 'is_content', 'in_rankings',
         'banner', 'banner_id', 'breaking_news'),
        css_class='column-right checkboxes')
    author_fields = gocept.form.grouped.Fields(
        _("Authors"),
        ('author_references', 'authors'),
         css_class='wide-widgets column-left')

    field_groups = (
        navigation_fields,
        head_fields,
        text_fields,
        gocept.form.grouped.RemainingFields(
            _("misc."),
            css_class='column-right'),
        author_fields,
        option_fields,
        )
    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata)

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

    @property
    def template(self):
        # Sneak in the javascript for copying teaser texts
        zc.resourcelibrary.need('zeit.cms.content.teaser')
        zc.resourcelibrary.need('zeit.cms.content.dropdown')
        return super(CommonMetadataFormBase, self).template


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
