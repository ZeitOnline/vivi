from zeit.cms.browser.widget import CheckboxDisplayWidget
from zeit.cms.browser.widget import RestructuredTextWidget
from zeit.cms.content.interfaces import ICommonMetadata
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.repository.interfaces import IAutomaticallyRenameable
from zeit.content.article.edit.interfaces import IEditableBody
from zeit.content.article.interfaces import IArticle
from zeit.content.author.interfaces import IAuthor
from zeit.content.gallery.interfaces import IGallery
from zeit.content.image.interfaces import IImageGroup
from zeit.workflow.publishinfo import id_to_principal
import zeit.cms.asset.interfaces
import zeit.cms.browser.interfaces
import zeit.cms.content.interfaces
import zeit.cms.related.interfaces
import zeit.cms.workflow.interfaces
import zeit.content.article.interfaces
import zeit.content.gallery.interfaces
import zeit.content.image.interfaces
import zeit.content.video.interfaces
import zeit.edit.browser.form
import zeit.workflow.interfaces
import zope.formlib.form
import zope.formlib.interfaces


class FormFields(zope.formlib.form.FormFields):

    def __init__(self, *args, **kw):
        kw.setdefault(
            'render_context', zope.formlib.interfaces.DISPLAY_UNWRITEABLE)
        super(FormFields, self).__init__(*args, **kw)


class Heading(object):

    def render(self):
        # workaround until the title is synchronized to the heading (#11255)
        if IAutomaticallyRenameable(self.context).renameable:
            return ''
        return super(Heading, self).render()


class MemoFormGroup(zeit.edit.browser.form.FormGroup):

    title = u''


class Memo(zeit.edit.browser.form.InlineForm):

    legend = u''
    prefix = 'memo'
    undo_description = _('edit memo')
    form_fields = FormFields(zeit.cms.content.interfaces.IMemo).select('memo')
    form_fields['memo'].custom_widget = RestructuredTextWidget
    css_class = 'memo'


class ArticleContentForms(zeit.edit.browser.form.FoldableFormGroup):
    """Article content forms."""

    title = _('Article')
    folded_workingcopy = False

    @property
    def body(self):
        return zeit.content.article.edit.interfaces.IEditableBody(
            self.context)


class ArticleContentHead(zeit.edit.browser.form.InlineForm,
                         zeit.cms.browser.form.CharlimitMixin):

    legend = _('')
    prefix = 'article-content-head'
    undo_description = _('edit article content head')
    form_fields = FormFields(ICommonMetadata).select(
        'supertitle', 'title', 'breadcrumb_title', 'subtitle')

    def setUpWidgets(self, *args, **kw):
        super(ArticleContentHead, self).setUpWidgets(*args, **kw)
        self.set_charlimit('supertitle')
        self.set_charlimit('title')
        self.set_charlimit('breadcrumb_title')
        self.set_charlimit('subtitle')

    def _success_handler(self):
        self.signal('reload-inline-view', 'edit.heading')


class ArticleContentMainImage(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'article-content-main-image'
    undo_description = _('edit article content main image')
    form_fields = FormFields(IArticle).select(
        'main_image', 'main_image_variant_name')

    def __call__(self):
        zope.interface.alsoProvides(
            self.request, zeit.cms.browser.interfaces.IGlobalSearchLayer)
        return super(ArticleContentMainImage, self).__call__()

    def _success_handler(self):
        # even though the image is not displayed in the body area,
        # the body still needs to be updated so it knows the (possibly) new
        # UUID of the image block
        body = IEditableBody(self.context)
        self.signal('reload', 'editable-body', self.url(body, 'contents'))


class KeywordsFormGroup(zeit.edit.browser.form.FoldableFormGroup):

    title = _('Keywords')

    def render(self):
        if not IAutomaticallyRenameable(self.context).renameable:
            return ''
        return super(KeywordsFormGroup, self).render()


class KeywordsNew(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'keywords'
    undo_description = _('edit keywords')
    css_class = 'keywords'
    form_fields = FormFields(IArticle).select('keywords')

    def render(self):
        if not IAutomaticallyRenameable(self.context).renameable:
            return ''
        return super(KeywordsNew, self).render()

    def setUpWidgets(self, *args, **kw):
        super(KeywordsNew, self).setUpWidgets(*args, **kw)
        self.widgets['keywords'].show_helptext = True


class FilenameFormGroup(zeit.edit.browser.form.FoldableFormGroup):

    title = _('Filename')

    def render(self):
        if not IAutomaticallyRenameable(self.context).renameable:
            return ''
        return super(FilenameFormGroup, self).render()


class NewFilename(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'new-filename'
    undo_description = _('edit new filename')
    css_class = 'table'

    @property
    def form_fields(self):
        form_fields = FormFields(
            zeit.cms.interfaces.ICMSContent,
            zeit.cms.repository.interfaces.IAutomaticallyRenameable,
            render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
                '__name__', 'rename_to')
        if zeit.cms.repository.interfaces.IAutomaticallyRenameable(
                self.context).renameable:
            form_fields = form_fields.omit('__name__')
        else:
            form_fields = form_fields.omit('rename_to')
        return form_fields


class LeadTeaserForms(zeit.edit.browser.form.FoldableFormGroup):

    title = _('Lead teaser')


class AssetBadges(zeit.edit.browser.form.InlineForm):

    legend = _('Badges')
    prefix = 'asset-badges'
    undo_description = _('edit asset badges')
    form_fields = FormFields(
        zeit.cms.asset.interfaces.IBadges).select('badges')

    def setUpWidgets(self, *args, **kw):
        super(AssetBadges, self).setUpWidgets(*args, **kw)
        self.widgets['badges'].orientation = 'horizontal'


class LeadTeaser(zeit.edit.browser.form.InlineForm):

    legend = ''
    prefix = 'leadteaser'
    undo_description = _('edit lead teaser')
    form_fields = FormFields(
        zeit.content.image.interfaces.IImages,
        zeit.content.gallery.interfaces.IGalleryReference,
        zeit.content.video.interfaces.IVideoAsset,
    )
    form_fields['fill_color'].custom_widget = (
        zeit.cms.browser.widget.ColorpickerWidget)

    def __call__(self):
        zope.interface.alsoProvides(
            self.request, zeit.cms.browser.interfaces.IGlobalSearchLayer)
        return super(LeadTeaser, self).__call__()

    def setUpWidgets(self, *args, **kw):
        super(LeadTeaser, self).setUpWidgets(*args, **kw)
        self.widgets['image'].add_type = IImageGroup
        self.widgets['gallery'].add_type = IGallery

    def _success_handler(self):
        self.signal('reload-inline-form', 'teaser-image')
        self.signal('reload-inline-form', 'article-content-main-image')
        body = IEditableBody(self.context)
        self.signal('reload', 'editable-body', self.url(body, 'contents'))


class InternalLinksForms(zeit.edit.browser.form.FoldableFormGroup):

    title = _('Internal links')


class InternalLinks(zeit.edit.browser.form.InlineForm):

    legend = ''
    prefix = 'internallinks'
    undo_description = _('edit internal links')
    form_fields = FormFields(
        zeit.cms.related.interfaces.IRelatedContent,
        zeit.content.article.interfaces.IAggregatedComments,
    )

    def setUpWidgets(self, *args, **kw):
        super(InternalLinks, self).setUpWidgets(*args, **kw)
        self.widgets['related'].detail_view_name = '@@related-details'

    def __call__(self):
        zope.interface.alsoProvides(
            self.request, zeit.cms.browser.interfaces.IGlobalSearchLayer)
        return super(InternalLinks, self).__call__()


class StatusForms(zeit.edit.browser.form.FoldableFormGroup):

    title = _('Status')


class WorkflowStatusDisplay(zeit.edit.browser.form.InlineForm):

    legend = _('')
    form_fields = FormFields(
        zeit.workflow.interfaces.IContentWorkflow).select(
            'edited', 'corrected', 'seo_optimized')
    form_fields['edited'].custom_widget = CheckboxDisplayWidget
    form_fields['corrected'].custom_widget = CheckboxDisplayWidget
    form_fields['seo_optimized'].custom_widget = CheckboxDisplayWidget


class LastPublished(object):

    @property
    def publishinfo(self):
        return zeit.cms.workflow.interfaces.IPublishInfo(self.context)

    @property
    def last_published_date(self):
        tz = zope.interface.common.idatetime.ITZInfo(self.request)
        return self.publishinfo.date_last_published.astimezone(tz)

    @property
    def date(self):
        return self.last_published_date.strftime('%d.%m.%Y')

    @property
    def time(self):
        return self.last_published_date.strftime('%H:%M')

    @property
    def last_published_by(self):
        principal = id_to_principal(self.publishinfo.last_published_by)
        return principal.title if principal else ''


class MetadataForms(zeit.edit.browser.form.FoldableFormGroup):
    """Metadata forms view."""

    title = _('Metadata')


class Keywords(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'keywords'
    undo_description = _('edit keywords')
    css_class = 'keywords'
    # XXX this should say ICommonMetadata, but InlineForm does not inherit from
    # cms.browser.form.EditForm, so form_fields are not post-processed to get
    # overriden fields
    form_fields = FormFields(IArticle).select('keywords')

    def __call__(self):
        if IAutomaticallyRenameable(self.context).renameable:
            return ''
        return super(Keywords, self).__call__()


class MetadataA(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'metadata-a'
    undo_description = _('edit metadata')
    form_fields = FormFields(ICommonMetadata).select('ressort', 'sub_ressort')

    def render(self):
        result = super(MetadataA, self).render()
        if result:
            result += (
                '<script type="text/javascript">'
                '    zeit.cms.configure_ressort_dropdown("%s.");'
                '</script>') % (self.prefix,)
        return result

    def _success_handler(self):
        self.signal('reload-inline-view', 'edit.heading')
        self.signal(
            'reload-inline-view', 'edit.form.article-content-suggest-keywords')
        self.signal('reload-inline-form', 'channel-selector')


class MetadataB(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'metadata-b'
    undo_description = _('edit metadata')
    form_fields = FormFields(ICommonMetadata).select('product', 'copyrights')


class MetadataC(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'metadata-c'
    undo_description = _('edit metadata')
    form_fields = FormFields(ICommonMetadata).select('authorships')

    def setUpWidgets(self, *args, **kw):
        super(MetadataC, self).setUpWidgets(*args, **kw)
        self.widgets['authorships'].add_type = IAuthor
        self.widgets['authorships'].display_list_below_buttons = True

    def _success_handler(self):
        self.signal('reload-inline-view', 'edit.heading')


class MetadataAcquisition(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'metadata-acquisition'
    undo_description = _('edit acquisition')
    form_fields = FormFields(ICommonMetadata).select('acquisition')


class MetadataGenre(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'metadata-genre'
    undo_description = _('edit metadata')
    form_fields = FormFields(IArticle).select('genre')


class MetadataNL(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'metadata-nl'
    undo_description = _('edit metadata')
    form_fields = FormFields(ICommonMetadata).select('dailyNewsletter')


class MetadataComments(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'metadata-comments'
    undo_description = _('edit metadata')

    @property
    def form_fields(self):
        fields = ('commentSectionEnable',)
        if self.context.commentSectionEnable:
            fields += ('commentsAllowed',)
        return FormFields(ICommonMetadata).select(*fields)


class TeaserForms(zeit.edit.browser.form.FoldableFormGroup):
    """Teaser workflow forms."""

    title = _('Teaser')


class TeaserImage(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'teaser-image'
    undo_description = _('edit teaser image')
    css_class = 'teaser-image'
    form_fields = FormFields(
        zeit.content.image.interfaces.IImages).select('image')

    def __call__(self):
        zope.interface.alsoProvides(
            self.request, zeit.cms.browser.interfaces.IGlobalSearchLayer)
        return super(TeaserImage, self).__call__()

    def setUpWidgets(self, *args, **kw):
        try:
            master = zeit.content.image.interfaces.IMasterImage(
                zeit.content.image.interfaces.IImages(self.context).image)
            if master.format == 'PNG' and (
                    self.form_fields.get('fill_color') is None):
                self.form_fields += FormFields(
                    zeit.content.image.interfaces.IImages).select('fill_color')
                self.form_fields['fill_color'].custom_widget = (
                    zeit.cms.browser.widget.ColorpickerWidget)
        except TypeError:
            self.form_fields = self.form_fields.omit('fill_color')
        super(TeaserImage, self).setUpWidgets(*args, **kw)
        self.widgets['image'].add_type = IImageGroup

    def _success_handler(self):
        self.signal('reload-inline-form', 'leadteaser')
        self.signal('reload-inline-form', 'article-content-main-image')
        body = IEditableBody(self.context)
        # XXX it would be nicer if we didn't need to know the reload URL here
        # (e.g. write it onto the DOM element)
        self.signal('reload', 'editable-body', self.url(body, 'contents'))


class TeaserSupertitle(zeit.edit.browser.form.InlineForm,
                       zeit.cms.browser.form.CharlimitMixin):

    legend = _('')
    prefix = 'teaser-supertitle'
    undo_description = _('edit teaser supertitle')
    form_fields = FormFields(ICommonMetadata).select('teaserSupertitle')

    def setUpWidgets(self, *args, **kw):
        super(TeaserSupertitle, self).setUpWidgets(*args, **kw)
        self.set_charlimit('teaserSupertitle')


class TeaserTitle(zeit.edit.browser.form.InlineForm,
                  zeit.cms.browser.form.CharlimitMixin):

    legend = _('')
    prefix = 'teaser-title'
    undo_description = _('edit teaser title')
    form_fields = FormFields(ICommonMetadata).select('teaserTitle')

    def setUpWidgets(self, *args, **kw):
        super(TeaserTitle, self).setUpWidgets(*args, **kw)
        self.set_charlimit('teaserTitle')


class TeaserText(zeit.edit.browser.form.InlineForm,
                 zeit.cms.browser.form.CharlimitMixin):

    legend = _('')
    prefix = 'teaser-text'
    undo_description = _('edit teaser text')
    form_fields = FormFields(ICommonMetadata).select('teaserText')

    def setUpWidgets(self, *args, **kw):
        super(TeaserText, self).setUpWidgets(*args, **kw)
        self.set_charlimit('teaserText')


class OptionFormGroup(zeit.edit.browser.form.FoldableFormGroup):

    title = _('Options')


class OptionsA(zeit.edit.browser.form.InlineForm):

    legend = ''
    prefix = 'options-a'
    undo_description = _('edit options')
    form_fields = FormFields(IArticle).select(
        'serie', 'breaking_news')


class OptionsB(zeit.edit.browser.form.InlineForm):

    legend = ''
    prefix = 'options-b'
    undo_description = _('edit options')
    form_fields = FormFields(ICommonMetadata).select(
        'year', 'volume', 'page', 'printRessort', 'byline')

    def setUpWidgets(self, *args, **kw):
        super(OptionsB, self).setUpWidgets(*args, **kw)
        # the 'page' field is an Int, so we can't use default='n/a'
        if not self.context.page:
            self.widgets['page'].setRenderedValue('n/a')

    def _success_handler(self):
        self.signal('reload-inline-view', 'edit.heading')


class OptionsC(zeit.edit.browser.form.InlineForm):

    legend = ''
    prefix = 'options-c'
    undo_description = _('edit options')
    form_fields = FormFields(ICommonMetadata).select(
        'mobile_alternative', 'deeplink_url')


class OptionsProductManagement(zeit.edit.browser.form.InlineForm):

    legend = _('Product management')
    prefix = 'options-productmanagement'
    undo_description = _('edit options')
    form_fields = FormFields(ICommonMetadata).select(
        'cap_title', 'banner_id', 'vg_wort_id',
        'advertisement_title', 'advertisement_text')


class OptionsProductManagementB(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'misc-product-management-b'
    undo_description = _('edit misc product management')
    form_fields = FormFields(ICommonMetadata).select(
        'minimal_header', 'in_rankings', 'is_content',
        'banner', 'countings')


class OptionsLayout(zeit.edit.browser.form.InlineForm):

    legend = ''
    prefix = 'options-layout'
    undo_description = _('edit options')
    form_fields = (
        FormFields(ICommonMetadata).select('color_scheme')
        + FormFields(IArticle).select('layout'))

    def __call__(self):
        zope.interface.alsoProvides(
            self.request, zeit.cms.browser.interfaces.IGlobalSearchLayer)
        return super(OptionsLayout, self).__call__()

    def setUpWidgets(self, *args, **kw):
        super(OptionsLayout, self).setUpWidgets(*args, **kw)
        self.widgets['layout'].display_search_button = False
        self.widgets['layout'].display_url_field = False


class ChannelFormGroup(zeit.edit.browser.form.FoldableFormGroup):

    title = _('Run in channel')


class LeadCandidate(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'lead-candidate'
    undo_description = _('select channel')
    form_fields = FormFields(ICommonMetadata).select('lead_candidate')


class ChannelSelector(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'channel-selector'
    undo_description = _('select channel')
    form_fields = FormFields(ICommonMetadata).select('channels')

    def render(self):
        result = super(ChannelSelector, self).render()
        if result:
            result += """\
<script type="text/javascript">
    zeit.cms.configure_channel_dropdowns("%s.", "channels", "00", "01");
</script>""" % (self.prefix,)
        return result

    # Generate an action name just like the SequenceWidget remove button.
    @zope.formlib.form.action('remove', prefix='channels')
    def submit_on_remove(self, action, data):
        """Trigger a save each time the remove button is pressed,
        since there is no other event for the inline form to do that."""
        super(ChannelSelector, self).handle_edit_action.success(data)

    @zope.formlib.form.action(
        _('Apply'), condition=zope.formlib.form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        """Once you override one action, you lose *all* inherited ones."""
        super(ChannelSelector, self).handle_edit_action.success(data)


class StorystreamFormGroup(zeit.edit.browser.form.FoldableFormGroup):

    title = _('Storystream')


class Tldr(zeit.edit.browser.form.InlineForm,
           zeit.cms.browser.form.CharlimitMixin):

    legend = _('')
    prefix = 'storystream'
    undo_description = _('edit storystream')
    form_fields = FormFields(ICommonMetadata).select(
        'tldr_title', 'tldr_text', 'tldr_milestone', 'tldr_date',
        'storystreams')

    def setUpWidgets(self, *args, **kw):
        super(Tldr, self).setUpWidgets(*args, **kw)
        self.set_charlimit('tldr_title')
        self.set_charlimit('tldr_text')

    # Generate an action name just like the SequenceWidget remove button.
    @zope.formlib.form.action('remove', prefix='storystreams')
    def submit_on_remove(self, action, data):
        """Trigger a save each time the remove button is pressed,
        since there is no other event for the inline form to do that."""
        super(Tldr, self).handle_edit_action.success(data)

    @zope.formlib.form.action(
        _('Apply'), condition=zope.formlib.form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        """Once you override one action, you lose *all* inherited ones."""
        super(Tldr, self).handle_edit_action.success(data)
