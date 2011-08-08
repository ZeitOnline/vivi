# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
from zope.app.form.browser.textwidgets import TextAreaWidget
import zeit.cms.asset.browser
import zeit.cms.browser.interfaces
import zeit.content.article.interfaces
import zope.app.pagetemplate
import zope.formlib.form
import zope.formlib.interfaces
import zope.interface


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
            self.context).renamable:
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

    def setUpWidgets(self):
        super(AssetBadges, self).setUpWidgets()
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


class LimitedInputWidget(zope.app.form.browser.textwidgets.TextAreaWidget):

    def __call__(self):
        max_length = self.context.max_length
        self.extra = 'data-limit="%s"' % max_length
        result = [
            '<span class="charlimit" />%s</span>' % max_length,
        super(LimitedInputWidget, self).__call__(),
            ('<script type="text/javascript">'
             '    jQuery(".charlimit").limitedInput()'
             '</script>')]


        return ''.join(result)


class TeaserText(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'teaser-text'
    undo_description = _('edit teaser text')

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata,
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
            'teaserText')
    form_fields['teaserText'].custom_widget = LimitedInputWidget


class MiscForms(zeit.edit.browser.form.FoldableFormGroup):
    """Miscellaneous"""

    title = _('Miscellaneous')


class MiscPrintdata(zeit.edit.browser.form.InlineForm):

    legend = _('Printdata')
    prefix = 'misc-printdata'
    undo_description = _('edit misc printdata')

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata,
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
            'year', 'volume', 'page')


class MiscFeatures(zeit.edit.browser.form.InlineForm):

    legend = _('Features')
    prefix = 'misc-features'
    undo_description = _('edit misc features')

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata,
        zeit.content.article.interfaces.ICDSWorkflow,
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
            'commentsAllowed', 'export_cds', 'serie')


class MiscProductManagementA(zeit.edit.browser.form.InlineForm):

    legend = _('Product Management')
    prefix = 'misc-product-management-a'
    undo_description = _('edit misc product management')

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata,
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
            'banner_id', 'cap_title', 'color_scheme')


class MiscProductManagementB(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'misc-product-management-b'
    undo_description = _('edit misc product management')

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata,
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
            'banner', 'countings')


class MiscLayout(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'misc-layout'
    undo_description = _('edit misc layout')

    def __call__(self):
        zope.interface.alsoProvides(
            self.request, zeit.cms.browser.interfaces.IGlobalSearchLayer)
        return super(MiscLayout, self).__call__()

    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.interfaces.IArticleMetadata,
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
            'layout')


class WorkflowForms(zeit.edit.browser.form.FoldableFormGroup):
    """Article workflow forms."""

    title = _('Workflow')


class WorkflowDates(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'workflow-dates'
    undo_description = _('edit workflow dates')
    css_class = 'table'

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.workflow.interfaces.IContentWorkflow,
            zeit.cms.workflow.interfaces.IModified,
            zeit.cms.content.interfaces.ISemanticChange,
            render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE) +
        zope.formlib.form.FormFields(
            zope.dublincore.interfaces.IDCTimes, for_display=True)).select(
                'last_modified_by', 'date_last_modified',
                'last_semantic_change', 'created')


class WorkflowStatus(zeit.edit.browser.form.InlineForm):

    legend = _('Status')
    prefix = 'workflow-status'
    undo_description = _('edit workflow status')

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.workflow.interfaces.IContentWorkflow,
            render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
                'published'))


class WorkflowPublicationDates(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'workflow-publication-dates'
    undo_description = _('edit workflow publication dates')
    css_class = 'table'

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.cms.workflow.interfaces.IPublishInfo,
            render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE) +
        zope.formlib.form.FormFields(
            zope.dublincore.interfaces.IDCTimes, for_display=True)).select(
                'date_last_published', 'date_first_released')


class WorkflowQualityAssurance(zeit.edit.browser.form.InlineForm):

    legend = _('Quality assurance')
    prefix = 'workflow-quality-assurance'
    undo_description = _('edit workflow quality assurance')
    css_class = 'table'

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.workflow.interfaces.IContentWorkflow,
            render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
                'edited', 'corrected', 'refined', 'images_added'))


class WorkflowPublicationPeriod(zeit.edit.browser.form.InlineForm):

    legend = _('Publication period')
    prefix = 'workflow-publication-period'
    undo_description = _('edit workflow publication period')

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.workflow.interfaces.IContentWorkflow,
            render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
                'release_period'))


class WorkflowLog(zeit.edit.browser.form.InlineForm):

    legend = _('Log')
    prefix = 'workflow-log'
    undo_description = None

    form_fields = zope.formlib.form.FormFields(
            zeit.objectlog.interfaces.ILog,
            render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE)


class ContextActionForms(zeit.edit.browser.form.FormGroup):
    """Article workflow forms."""

    title = _('Cotext action')


class Urgent(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'urgent'
    undo_description = _('edit urgent')

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.workflow.interfaces.IContentWorkflow,
            render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
                'urgent'))


class ContextAction(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'context action'
    undo_description = _('context action')
    template = zope.app.pagetemplate.ViewPageTemplateFile('context-action.pt')

    form_fields = ()

    def __call__(self):
        ci_manager = zeit.cms.checkout.interfaces.ICheckinManager(self.context)
        self.can_checkin = ci_manager.canCheckin
        co_manager = zeit.cms.checkout.interfaces.ICheckoutManager(self.context)
        self.can_checkout = co_manager.canCheckout
        publish_info = zeit.cms.workflow.interfaces.IPublishInfo(self.context)
        self.published = publish_info.published
        return super(ContextAction, self).__call__()


class Preview(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'preview'
    undo_description = _('edit preview')
