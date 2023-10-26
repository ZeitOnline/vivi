from zeit.cms.browser.widget import CheckboxDisplayWidget
from zeit.cms.browser.widget import RestructuredTextWidget
from zeit.cms.content.interfaces import ICommonMetadata, IRemoteMetadata
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.repository.interfaces import IAutomaticallyRenameable
from zeit.content.article.interfaces import IArticle
from zeit.content.author.interfaces import IAuthor
from zeit.content.image.interfaces import IImageGroup
from zeit.workflow.publishinfo import id_to_principal
import zeit.cms.browser.interfaces
import zeit.cms.content.interfaces
import zeit.cms.related.interfaces
import zeit.cms.workflow.interfaces
import zeit.content.article.interfaces
import zeit.content.gallery.interfaces
import zeit.content.image.interfaces
import zeit.content.video.interfaces
import zeit.content.audio.interfaces
import zeit.edit.browser.form
import zeit.workflow.interfaces
import zope.formlib.form
import zope.formlib.interfaces


class FormFields(zope.formlib.form.FormFields):

    def __init__(self, *args, **kw):
        kw.setdefault(
            'render_context', zope.formlib.interfaces.DISPLAY_UNWRITEABLE)
        super().__init__(*args, **kw)


class Heading:

    def render(self):
        # workaround until the title is synchronized to the heading (#11255)
        if IAutomaticallyRenameable(self.context).renameable:
            return ''
        return super().render()


class MemoFormGroup(zeit.edit.browser.form.FormGroup):

    title = ''


class Memo(zeit.edit.browser.form.InlineForm):

    legend = ''
    prefix = 'memo'
    form_fields = FormFields(zeit.cms.content.interfaces.IMemo).select('memo')
    form_fields['memo'].custom_widget = RestructuredTextWidget
    css_class = 'memo'


class ArticleContentForms(zeit.edit.browser.form.FoldableFormGroup):
    """Article content forms."""

    title = _('Article')
    folded_workingcopy = False


class ArticleContentHead(zeit.edit.browser.form.InlineForm,
                         zeit.cms.browser.form.CharlimitMixin):

    legend = _('')
    prefix = 'article-content-head'
    form_fields = FormFields(ICommonMetadata).select(
        'supertitle', 'title', 'subtitle')

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        self.set_charlimit('supertitle')
        self.set_charlimit('title')
        self.set_charlimit('subtitle')

    def _success_handler(self):
        self.signal('reload-inline-view', 'edit.heading')


class ArticleContentMainImage(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'article-content-main-image'
    form_fields = FormFields(IArticle).select(
        'main_image', 'main_image_variant_name')

    def __call__(self):
        zope.interface.alsoProvides(
            self.request, zeit.cms.browser.interfaces.IGlobalSearchLayer)
        return super().__call__()

    def _success_handler(self):
        # even though the image is not displayed in the body area,
        # the body still needs to be updated so it knows the (possibly) new
        # UUID of the image block
        self.signal(
            'reload', 'editable-body', self.url(self.context.body, 'contents'))


class KeywordsFormGroup(zeit.edit.browser.form.FoldableFormGroup):

    title = _('Keywords')


class Keywords(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'keywords'
    css_class = 'keywords'
    form_fields = FormFields(IArticle).select('keywords')


class FilenameFormGroup(zeit.edit.browser.form.FoldableFormGroup):

    title = _('Filename')

    def render(self):
        if not IAutomaticallyRenameable(self.context).renameable:
            return ''
        return super().render()


class NewFilename(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'new-filename'
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


class InternalLinksForms(zeit.edit.browser.form.FoldableFormGroup):

    title = _('Internal links')


class InternalLinks(zeit.edit.browser.form.InlineForm):

    legend = ''
    prefix = 'internallinks'
    form_fields = FormFields(zeit.cms.related.interfaces.IRelatedContent)
    form_fields += FormFields(
        zeit.content.article.interfaces.IArticleMetadata
    ).select('hide_ligatus_recommendations', 'prevent_ligatus_indexing')

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        self.widgets['related'].detail_view_name = '@@related-details'

    def __call__(self):
        zope.interface.alsoProvides(
            self.request, zeit.cms.browser.interfaces.IGlobalSearchLayer)
        return super().__call__()


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


class LastPublished:

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
        return id_to_principal(self.publishinfo.last_published_by)


class MetadataForms(zeit.edit.browser.form.FoldableFormGroup):
    """Metadata forms view."""

    title = _('Metadata')


class MetadataA(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'metadata-a'
    form_fields = FormFields(ICommonMetadata).select('ressort', 'sub_ressort')

    def render(self):
        result = super().render()
        if result:
            result += (
                '<script type="text/javascript">'
                '    zeit.cms.configure_ressort_dropdown("%s.");'
                '</script>') % (self.prefix,)
        return result

    def _success_handler(self):
        self.signal('reload-inline-view', 'edit.heading')
        self.signal('reload-inline-form', 'channel-selector')


class MetadataB(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'metadata-b'
    form_fields = FormFields(ICommonMetadata).select('product', 'copyrights')


class MetadataC(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'metadata-c'
    form_fields = FormFields(ICommonMetadata).select('authorships')

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        self.widgets['authorships'].add_type = IAuthor
        self.widgets['authorships'].display_list_below_buttons = True

    def _success_handler(self):
        self.signal('reload-inline-view', 'edit.heading')


class MetadataAgency(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'metadata-agency'
    form_fields = FormFields()

    def __init__(self, context, request):
        super().__init__(context, request)
        if FEATURE_TOGGLES.find('article_agencies'):
            self.form_fields = FormFields(ICommonMetadata).select('agencies')


class MetadataAccess(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'metadata-access'
    form_fields = FormFields(ICommonMetadata).select('access')

    def _success_handler(self):
        self.signal('reload-inline-form', 'social')


class MetadataGenre(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'metadata-genre'
    form_fields = FormFields(IArticle).select('genre')

    def _success_handler(self):
        self.signal('reload-inline-form', 'recipe-categories')
        self.signal('reload-inline-form', 'options-audio-speechbert')


class CommentsFormGroup(zeit.edit.browser.form.FoldableFormGroup):

    title = _('Comments')


class Comments(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'metadata-comments'

    @property
    def form_fields(self):
        fields = ('commentSectionEnable',)
        if self.context.commentSectionEnable:
            fields += (
                'commentsAllowed', 'commentsPremoderate', 'comments_sorting')
        return FormFields(IArticle).select(*fields)


class OptionsAudioSpeechbert(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'options-audio-speechbert'
    form_fields = FormFields(IArticle).select('audio_speechbert')
    css_class = 'audio-speechbert'


class TeaserForms(zeit.edit.browser.form.FoldableFormGroup):
    """Teaser workflow forms."""

    title = _('Teaser')


class TeaserImage(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'teaser-image'
    css_class = 'teaser-image'
    form_fields = FormFields(
        zeit.content.image.interfaces.IImages).select('image')

    def __call__(self):
        zope.interface.alsoProvides(
            self.request, zeit.cms.browser.interfaces.IGlobalSearchLayer)
        return super().__call__()

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
        super().setUpWidgets(*args, **kw)
        self.widgets['image'].add_type = IImageGroup

    def _success_handler(self):
        self.signal('reload-inline-form', 'article-content-main-image')
        self.signal('reload-inline-form', 'mobile')
        # XXX it would be nicer if we didn't need to know the reload URL here
        # (e.g. write it onto the DOM element)
        self.signal(
            'reload', 'editable-body', self.url(self.context.body, 'contents'))


class TeaserSupertitle(zeit.edit.browser.form.InlineForm,
                       zeit.cms.browser.form.CharlimitMixin):

    legend = _('')
    prefix = 'teaser-supertitle'
    form_fields = FormFields(ICommonMetadata).select('teaserSupertitle')

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        self.set_charlimit('teaserSupertitle')


class TeaserTitle(zeit.edit.browser.form.InlineForm,
                  zeit.cms.browser.form.CharlimitMixin):

    legend = _('')
    prefix = 'teaser-title'
    form_fields = FormFields(ICommonMetadata).select('teaserTitle')

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        self.set_charlimit('teaserTitle')


class TeaserText(zeit.edit.browser.form.InlineForm,
                 zeit.cms.browser.form.CharlimitMixin):

    legend = _('')
    prefix = 'teaser-text'
    form_fields = FormFields(ICommonMetadata).select('teaserText')

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        self.set_charlimit('teaserText')


class OptionFormGroup(zeit.edit.browser.form.FoldableFormGroup):

    title = _('Options')


class OptionsA(zeit.edit.browser.form.InlineForm):

    legend = ''
    prefix = 'options-a'
    form_fields = FormFields(IArticle).select('serie')


class OptionsB(zeit.edit.browser.form.InlineForm):

    legend = ''
    prefix = 'options-b'
    form_fields = FormFields(ICommonMetadata).select(
        'year', 'volume', 'page', 'printRessort', 'byline')

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        # the 'page' field is an Int, so we can't use default='n/a'
        if not self.context.page:
            self.widgets['page'].setRenderedValue('n/a')

    def _success_handler(self):
        self.signal('reload-inline-view', 'edit.heading')


class OptionsC(zeit.edit.browser.form.InlineForm):

    legend = ''
    prefix = 'options-c'
    form_fields = FormFields(ICommonMetadata).select(
        'deeplink_url', 'color_scheme')


class OptionsProductManagement(zeit.edit.browser.form.InlineForm):

    legend = _('Product management')
    prefix = 'options-productmanagement'
    form_fields = FormFields(ICommonMetadata).select(
        'cap_title', 'banner_id', 'vg_wort_id',
        'advertisement_title', 'advertisement_text')


class OptionsInteractive(zeit.edit.browser.form.InlineForm):

    legend = _('Interactive')
    prefix = 'options-interactive'
    form_fields = FormFields(IRemoteMetadata).select(
        'remote_image', 'remote_timestamp'
    )


class OptionsProductManagementB(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'misc-product-management-b'
    form_fields = FormFields(ICommonMetadata).select('overscrolling')


class RecipeCategories(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'recipe-categories'
    css_class = 'recipe-categories'
    form_fields = FormFields(IArticle).select('recipe_categories')
    recipe_genres = ['rezept', 'rezept-vorstellung']

    def render(self):
        if IArticle(self.context).genre in RecipeCategories.recipe_genres:
            return super().render()
        # Need to preserve the id for js to still be able to perform
        # reload-inline-form after it has been cleared once.
        return '<fieldset id="form-recipe-categories" />'


class ChannelFormGroup(zeit.edit.browser.form.FoldableFormGroup):

    title = _('Run in channel')


class ChannelSelector(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'channel-selector'
    form_fields = FormFields(ICommonMetadata).select('channels')

    def render(self):
        result = super().render()
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
        super().handle_edit_action.success(data)

    @zope.formlib.form.action(
        _('Apply'), condition=zope.formlib.form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        """Once you override one action, you lose *all* inherited ones."""
        super().handle_edit_action.success(data)


class AudioForms(zeit.edit.browser.form.FoldableFormGroup):

    title = _('Audio')


class Audio(zeit.edit.browser.form.InlineForm):

    legend = ''
    prefix = 'audio'
    form_fields = FormFields(zeit.content.audio.interfaces.IAudios)

    def __call__(self):
        zope.interface.alsoProvides(
            self.request, zeit.cms.browser.interfaces.IGlobalSearchLayer)
        return super().__call__()
