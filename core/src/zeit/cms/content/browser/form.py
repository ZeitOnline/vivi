from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import zeit.cms.browser.form
import zeit.cms.content.interfaces
import zeit.cms.settings.interfaces
import zope.formlib.form


class CommonMetadataFormBase(zeit.cms.browser.form.CharlimitMixin):

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
        ('commentsAllowed', 'commentSectionEnable',
         'banner_id', 'overscrolling'),
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
        zeit.cms.content.interfaces.ICommonMetadata)

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        self.set_charlimit('teaserText')


class CommonMetadataAddForm(CommonMetadataFormBase,
                            zeit.cms.browser.form.AddForm):
    """Add form which contains the common metadata."""

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        settings = zeit.cms.settings.interfaces.IGlobalSettings(self.context)
        if not self.widgets['year'].hasInput():
            self.widgets['year'].setRenderedValue(settings.default_year)
        if not self.widgets['volume'].hasInput():
            self.widgets['volume'].setRenderedValue(settings.default_volume)


class CommonMetadataEditForm(CommonMetadataFormBase,
                             zeit.cms.browser.form.EditForm):
    """Edit form which contains the common metadata."""


class CommonMetadataDisplayForm(CommonMetadataFormBase,
                                zeit.cms.browser.form.DisplayForm):
    """Display form which contains the common metadata."""
