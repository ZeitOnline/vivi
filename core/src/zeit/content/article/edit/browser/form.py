# Copyright (c) 2010-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.browser.widget import CheckboxDisplayWidget
from zeit.cms.browser.widget import RestructuredTextWidget
from zeit.cms.i18n import MessageFactory as _
from zeit.content.author.interfaces import IAuthor
from zeit.content.gallery.interfaces import IGallery
from zeit.content.image.interfaces import IImageGroup
from zeit.content.infobox.interfaces import IInfobox
from zeit.content.portraitbox.interfaces import IPortraitbox
import zeit.cms.browser.interfaces
import zeit.content.article.interfaces
import zope.formlib.form
import zope.formlib.interfaces


class DiverFormGroup(zeit.edit.browser.form.DiverFormGroup):
    """ Contains  """

    title = _('Diver')


class MemoDiver(zeit.edit.browser.form.DiverForm):

    legend = _('Memo')
    prefix = 'memo-diver'
    undo_description = _('edit memo')

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.IMemo,
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
            'memo')

    form_fields['memo'].custom_widget = RestructuredTextWidget


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

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata,
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
            'supertitle', 'title', 'subtitle')

    def render(self):
        result = super(ArticleContentHead, self).render()
        if result:
            result += (
                '<script type="text/javascript">'
                '    jQuery("#article-editor-text").countedInput();'
                '</script>')
        return result


class ArticleContentBody(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'article-content-body'
    undo_description = _('edit article content body')


class FilenameFormGroup(zeit.edit.browser.form.FormGroup):
    """ Filename view. """

    title = _('Filename')


class NewFilename(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'new-filename'
    undo_description = _('edit new filename')
    css_class = 'table'

    @property
    def form_fields(self):
        form_fields = zope.formlib.form.FormFields(
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


class AssetForms(zeit.edit.browser.form.FoldableFormGroup):
    """Article asset forms."""

    title = _('Assets')


class AssetBadges(zeit.edit.browser.form.InlineForm):

    legend = _('Badges')
    prefix = 'asset-badges'
    undo_description = _('edit asset badges')

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.asset.interfaces.IBadges,
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
            'badges')

    def setUpWidgets(self, *args, **kw):
        super(AssetBadges, self).setUpWidgets(*args, **kw)
        self.widgets['badges'].orientation = 'horizontal'


class Assets(zeit.edit.browser.form.InlineForm):

    legend = _('Assets')
    prefix = 'assets'
    undo_description = _('edit assets')

    def __call__(self):
        zope.interface.alsoProvides(
            self.request, zeit.cms.browser.interfaces.IGlobalSearchLayer)
        return super(Assets, self).__call__()

    @property
    def form_fields(self):
        interfaces = []
        for name, interface in zope.component.getUtilitiesFor(
            zeit.cms.asset.interfaces.IAssetInterface):
            interfaces.append(interface)
        return zope.formlib.form.FormFields(
            *interfaces,
            render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).omit(
                'badges')

    def setUpWidgets(self, *args, **kw):
        super(Assets, self).setUpWidgets(*args, **kw)
        self.widgets['images'].add_type = IImageGroup
        self.widgets['gallery'].add_type = IGallery
        self.widgets['portraitbox'].add_type = IPortraitbox
        self.widgets['infobox'].add_type = IInfobox


class StatusForms(zeit.edit.browser.form.FoldableFormGroup):

    title = _('Status')


class WorkflowStatusDisplay(zeit.edit.browser.form.InlineForm):

    legend = _('')
    form_fields = zope.formlib.form.FormFields(
        zeit.workflow.interfaces.IContentWorkflow,
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE
        ).select('edited', 'corrected')
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
        return self.publishinfo.date_last_published.strftime('%M:%H')


class MetadataForms(zeit.edit.browser.form.FoldableFormGroup):
    """Metadata forms view."""

    title = _('Metadata')


# This will be renamed properly as soon as the fields are finally decided.
class MetadataA(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'metadata-a'
    undo_description = _('edit metadata')
    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata,
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
            'ressort', 'sub_ressort', 'keywords')

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
    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata,
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
            'product', 'copyrights', 'dailyNewsletter')


# This will be renamed properly as soon as the fields are finally decided.
class MetadataC(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'metadata-c'
    undo_description = _('edit metadata')

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata,
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
            'author_references')

    def setUpWidgets(self, *args, **kw):
        super(MetadataC, self).setUpWidgets(*args, **kw)
        self.widgets['author_references'].detail_view_name = '@@author-details'
        self.widgets['author_references'].add_type = IAuthor


class TeaserForms(zeit.edit.browser.form.FoldableFormGroup):
    """Teaser workflow forms."""

    title = _('Teaser')


class TeaserTitle(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'teaser-title'
    undo_description = _('edit teaser title')

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata,
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
            'teaserTitle')


class TeaserText(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'teaser-text'
    undo_description = _('edit teaser text')
    css_class = 'limited-input'

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata,
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
            'teaserText')

    def render(self):
        result = super(TeaserText, self).render()
        if result:
            max_length = self.widgets['teaserText'].context.max_length
            result += (
                '<script type="text/javascript">'
                '    jQuery(".limited-input").limitedInput(%s)'
                '</script>' % max_length)
        return result


class MiscForms(zeit.edit.browser.form.FoldableFormGroup):

    title = _('Options')


class OptionsA(zeit.edit.browser.form.InlineForm):

    legend = ''
    prefix = 'options-a'
    undo_description = _('edit options')

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata).select(
        'serie', 'breaking_news')


class OptionsB(zeit.edit.browser.form.InlineForm):

    legend = ''
    prefix = 'options-b'
    undo_description = _('edit options')

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata,
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
            'year', 'volume', 'page', 'printRessort')


class OptionsProductManagement(zeit.edit.browser.form.InlineForm):

    legend = _('Product management')
    prefix = 'options-productmanagement'
    undo_description = _('edit options')

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata).select(
            'cap_title', 'banner_id', 'vg_wort_id')


class OptionsProductManagementB(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'misc-product-management-b'
    undo_description = _('edit misc product management')

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata).select(
            'minimal_header', 'in_rankings', 'is_content',
            'banner', 'countings')


class OptionsLayout(zeit.edit.browser.form.InlineForm):

    legend = ''
    prefix = 'options-layout'
    undo_description = _('edit options')

    def __call__(self):
        zope.interface.alsoProvides(
            self.request, zeit.cms.browser.interfaces.IGlobalSearchLayer)
        return super(OptionsLayout, self).__call__()

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata).select(
            'color_scheme') + zope.formlib.form.FormFields(
        zeit.content.article.interfaces.IArticleMetadata).select(
            'layout')
