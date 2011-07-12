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


class ArticleContentForms(zeit.edit.browser.form.FormGroup):
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


class AssetForms(zeit.edit.browser.form.FormGroup):
    """Article asset forms."""

    title = _('Assets')


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


class MetadataForms(zeit.edit.browser.form.FormGroup):
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

    @property
    def form_fields(self):
        form_fields = zope.formlib.form.FormFields(
            zeit.cms.interfaces.ICMSContent,
            zeit.cms.content.interfaces.ICommonMetadata,
            zeit.cms.repository.interfaces.IAutomaticallyRenameable,
            render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
                'author_references', 'rename_to', '__name__')
        if zeit.cms.repository.interfaces.IAutomaticallyRenameable(
            self.context).renamable:
            form_fields = form_fields.omit('__name__')
        else:
            form_fields = form_fields.omit('rename_to')
        return form_fields


class TeaserForms(zeit.edit.browser.form.FormGroup):
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


class MiscForms(zeit.edit.browser.form.FormGroup):
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


class WorkflowForms(zeit.edit.browser.form.FormGroup):
    """Article workflow forms."""

    title = _('Workflow')


class WorkflowStatus(zeit.edit.browser.form.InlineForm):

    legend = _('Status')
    prefix = 'workflow-status'
    undo_description = _('edit workflow status')

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.workflow.interfaces.IContentWorkflow,
            zeit.cms.workflow.interfaces.IModified,
            zeit.cms.content.interfaces.ISemanticChange,
            render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE) +
        zope.formlib.form.FormFields(
            zope.dublincore.interfaces.IDCTimes, for_display=True)).select(
                'last_modified_by', 'date_last_modified',
                'last_semantic_change', 'created',
                'published', 'date_last_published', 'date_first_released',
                'edited', 'corrected', 'refined', 'images_added')


class WorkflowSettings(zeit.edit.browser.form.InlineForm):

    legend = _('Settings')
    prefix = 'workflow-settings'
    undo_description = _('edit workflow settings')

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.workflow.interfaces.IContentWorkflow,
            zeit.content.article.interfaces.ICDSWorkflow,
            render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
                'release_period', 'urgent', 'export_cds'))


class WorkflowLog(zeit.edit.browser.form.InlineForm):

    legend = _('Log')
    prefix = 'workflow-log'
    undo_description = None

    form_fields = zope.formlib.form.FormFields(
            zeit.objectlog.interfaces.ILog,
            render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE)
