from zeit.cms.checkout.interfaces import ILocalContent
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
        ('channels',),
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


class CommonMetadataEditForm(CommonMetadataFormBase,
                             zeit.cms.browser.form.EditForm):
    """Edit form which contains the common metadata."""


class CommonMetadataDisplayForm(CommonMetadataFormBase,
                                zeit.cms.browser.form.DisplayForm):
    """Display form which contains the common metadata."""


class DispatchToViewOrEdit(zeit.cms.browser.view.Base):

    def __call__(self):
        in_repository = not ILocalContent.providedBy(self.context)
        existing_checkout = self._find_checked_out()
        if in_repository and existing_checkout:
            self.redirect(self.url(existing_checkout))
        else:
            view = zope.component.getMultiAdapter(
                (self.context, self.request), name='edit.html')
            return view()

    def _find_checked_out(self):
        for item in zeit.cms.checkout.interfaces.IWorkingcopy(None).values():
            if not zeit.cms.interfaces.ICMSContent.providedBy(item):
                continue
            if item.uniqueId == self.context.uniqueId:
                return item
