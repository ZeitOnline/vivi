# Copyright (c) 2010-2012 gocept gmbh & co. kg
# See also LICENSE.txt

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
import zeit.cms.browser.interfaces
import zeit.cms.checkout.interfaces
import zeit.cms.related.interfaces
import zeit.content.gallery.interfaces
import zeit.content.video.interfaces
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

    @property
    def body(self):
        return zeit.content.article.edit.interfaces.IEditableBody(
            self.context)


class ArticleContentHead(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'article-content-head'
    undo_description = _('edit article content head')
    form_fields = FormFields(ICommonMetadata).select(
        'supertitle', 'title', 'subtitle')

    def setUpWidgets(self, *args, **kw):
        super(ArticleContentHead, self).setUpWidgets(*args, **kw)
        self.widgets['title'].extra = 'cms:maxlength="%s"' % (
            self.widgets['title'].context.max_length)
        self.widgets['subtitle'].extra = 'cms:maxlength="%s"' % (
            self.widgets['subtitle'].context.max_length)


class ArticleContentBody(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'article-content-body'
    undo_description = _('edit article content body')


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
    form_fields = FormFields(ICommonMetadata).select('keywords')

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
    folded_workingcopy = True
    folded_repository = True


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
    folded_workingcopy = True
    form_fields = FormFields(
        zeit.content.image.interfaces.IImages,
        zeit.content.gallery.interfaces.IGalleryReference,
        zeit.content.video.interfaces.IVideoAsset,
    )

    def __call__(self):
        zope.interface.alsoProvides(
            self.request, zeit.cms.browser.interfaces.IGlobalSearchLayer)
        return super(LeadTeaser, self).__call__()

    def setUpWidgets(self, *args, **kw):
        super(LeadTeaser, self).setUpWidgets(*args, **kw)
        self.widgets['image'].add_type = IImageGroup
        self.widgets['gallery'].add_type = IGallery

    @zope.formlib.form.action(_('Apply'))
    def handle_edit_action(self, action, data):
        self.signal('reload-inline-form', 'teaser-image')
        body = IEditableBody(self.context)
        self.signal('reload', 'editable-body', self.url(body, 'contents'))
        return super(LeadTeaser, self).handle_edit_action.success(data)


class InternalLinksForms(zeit.edit.browser.form.FoldableFormGroup):

    title = _('Internal links')

    def render(self):
        if not zeit.cms.checkout.interfaces.ILocalContent.providedBy(
            self.context):
            return ''
        return super(InternalLinksForms, self).render()


class InternalLinks(zeit.edit.browser.form.InlineForm):

    legend = ''
    prefix = 'internallinks'
    undo_description = _('edit internal links')
    form_fields = FormFields(
        zeit.cms.related.interfaces.IRelatedContent,
        zeit.content.article.interfaces.IAggregatedComments,
    )

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
        'edited', 'corrected')
    form_fields['edited'].custom_widget = CheckboxDisplayWidget
    form_fields['corrected'].custom_widget = CheckboxDisplayWidget


class LastPublished(object):

    @property
    def publishinfo(self):
        return zeit.cms.workflow.interfaces.IPublishInfo(self.context)

    @property
    def date(self):
        return self.publishinfo.date_last_published.strftime('%d.%m.%Y')

    @property
    def time(self):
        return self.publishinfo.date_last_published.strftime('%H:%M')


class MetadataForms(zeit.edit.browser.form.FoldableFormGroup):
    """Metadata forms view."""

    title = _('Metadata')
    folded_repository = True


class Keywords(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'keywords'
    undo_description = _('edit keywords')
    css_class = 'keywords'
    form_fields = FormFields(ICommonMetadata).select('keywords')

    def __call__(self):
        if IAutomaticallyRenameable(self.context).renameable:
            return ''
        return super(Keywords, self).__call__()


# This will be renamed properly as soon as the fields are finally decided.
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


# This will be renamed properly as soon as the fields are finally decided.
class MetadataB(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'metadata-b'
    undo_description = _('edit metadata')
    form_fields = FormFields(ICommonMetadata).select('product', 'copyrights')


# This will be renamed properly as soon as the fields are finally decided.
class MetadataC(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'metadata-c'
    undo_description = _('edit metadata')
    form_fields = FormFields(ICommonMetadata).select('author_references')

    def setUpWidgets(self, *args, **kw):
        super(MetadataC, self).setUpWidgets(*args, **kw)
        self.widgets['author_references'].detail_view_name = '@@author-details'
        self.widgets['author_references'].add_type = IAuthor
        self.widgets['author_references'].display_list_below_buttons = True


class MetadataNL(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'metadata-nl'
    undo_description = _('edit metadata')
    form_fields = FormFields(ICommonMetadata).select('dailyNewsletter')


class MetadataComments(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'metadata-comments'
    undo_description = _('edit metadata')
    form_fields = FormFields(ICommonMetadata).select(
        'commentSectionEnable', 'commentsAllowed')


class MetadataRecensions(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'metadata-recensions'
    undo_description = _('edit metadata')
    form_fields = FormFields(IArticle).select(
        'has_recensions')


class TeaserForms(zeit.edit.browser.form.FoldableFormGroup):
    """Teaser workflow forms."""

    title = _('Teaser')
    folded_repository = True


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
        super(TeaserImage, self).setUpWidgets(*args, **kw)
        self.widgets['image'].add_type = IImageGroup

    @zope.formlib.form.action(_('Apply'))
    def handle_edit_action(self, action, data):
        self.signal('reload-inline-form', 'leadteaser')
        body = IEditableBody(self.context)
        # XXX it would be nicer if we didn't need to know the reload URL here
        # (e.g. write it onto the DOM element)
        self.signal('reload', 'editable-body', self.url(body, 'contents'))
        return super(TeaserImage, self).handle_edit_action.success(data)


class TeaserSupertitle(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'teaser-supertitle'
    undo_description = _('edit teaser supertitle')
    form_fields = FormFields(ICommonMetadata).select('teaserSupertitle')

    def setUpWidgets(self, *args, **kw):
        super(TeaserSupertitle, self).setUpWidgets(*args, **kw)
        self.widgets['teaserSupertitle'].extra = 'cms:maxlength="%s"' % (
            self.widgets['teaserSupertitle'].context.max_length)


class TeaserTitle(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'teaser-title'
    undo_description = _('edit teaser title')
    form_fields = FormFields(ICommonMetadata).select('teaserTitle')

    def setUpWidgets(self, *args, **kw):
        super(TeaserTitle, self).setUpWidgets(*args, **kw)
        self.widgets['teaserTitle'].extra = 'cms:maxlength="%s"' % (
            self.widgets['teaserTitle'].context.max_length)


class TeaserText(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'teaser-text'
    undo_description = _('edit teaser text')
    form_fields = FormFields(ICommonMetadata).select('teaserText')

    def setUpWidgets(self, *args, **kw):
        super(TeaserText, self).setUpWidgets(*args, **kw)
        self.widgets['teaserText'].extra = 'cms:maxlength="%s"' % (
            self.widgets['teaserText'].context.max_length)


class MiscForms(zeit.edit.browser.form.FoldableFormGroup):

    title = _('Options')
    folded_workingcopy = True
    folded_repository = True


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
        'year', 'volume', 'page', 'printRessort')

    def setUpWidgets(self, *args, **kw):
        super(OptionsB, self).setUpWidgets(*args, **kw)
        # the 'page' field is an Int, so we can't use default='n/a'
        if not self.context.page:
            self.widgets['page'].setRenderedValue('n/a')


class OptionsProductManagement(zeit.edit.browser.form.InlineForm):

    legend = _('Product management')
    prefix = 'options-productmanagement'
    undo_description = _('edit options')
    form_fields = FormFields(ICommonMetadata).select(
        'cap_title', 'banner_id', 'vg_wort_id')


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
