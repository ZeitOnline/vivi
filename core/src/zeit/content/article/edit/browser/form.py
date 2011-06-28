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


class ArticleForms(object):
    """View which includes all article forms."""


class InlineForm(zope.formlib.form.SubPageEditForm,
                 zeit.edit.browser.view.UndoableMixin):

    template = zope.app.pagetemplate.ViewPageTemplateFile('edit.inlineform.pt')

    def __call__(self):
        self.mark_transaction_undoable()
        return super(InlineForm, self).__call__()

    @property
    def widget_data(self):
        result = []
        for widget in self.widgets:
            css_class = ['widget-outer']
            if widget.error():
                css_class.append('error')
            result.append(dict(
                css_class=' '.join(css_class),
                widget=widget,
            ))
        return result


class ArticleContentForms(object):
    """Article content forms."""

    title = _('Article')

    @property
    def body(self):
        return zeit.content.article.edit.interfaces.IEditableBody(
            self.context)


class ArticleContentHead(InlineForm):

    legend = _('')
    prefix = 'article-content-head'
    undo_description = _('edit article content head')

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata,
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
            'supertitle', 'title', 'subtitle')


class ArticleContentBody(InlineForm):

    legend = _('')
    prefix = 'article-content-body'
    undo_description = _('edit article content body')




class AssetForms(object):
    """Article asset forms."""

    title = _('Assets')


class Assets(InlineForm):

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


class MetadataForms(object):
    """Metadata forms view."""

    title = _('Metadata')


# This will be renamed properly as soon as the fields are finally decided.
class MetadataA(InlineForm):

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
class MetadataB(InlineForm):

    legend = _('')
    prefix = 'metadata-b'
    undo_description = _('edit metadata')
    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata,
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
            'product', 'copyrights', 'dailyNewsletter')

    def render(self):
        result = super(MetadataB, self).render()
        if result:
            result += (
                '<script type="text/javascript">'
                '    zeit.cms.configure_ressort_dropdown("%s.");'
                '</script>') % (self.prefix,)
        return result


# This will be renamed properly as soon as the fields are finally decided.
class MetadataC(InlineForm):

    legend = _('')
    prefix = 'metadata-c'
    undo_description = _('edit metadata')
    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata,
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
            'authors')

    def render(self):
        result = super(MetadataC, self).render()
        if result:
            result += (
                '<script type="text/javascript">'
                '    zeit.cms.configure_ressort_dropdown("%s.");'
                '</script>') % (self.prefix,)
        return result


class TeaserForms(object):
    """Teaser workflow forms."""

    title = _('Teaser')


class TeaserTitle(InlineForm):

    legend = _('')
    prefix = 'teaser-title'
    undo_description = _('edit teaser title')

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata,
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
            'teaserTitle')

    def render(self):
        result = super(TeaserTitle, self).render()
        if result:
            result += (
                '<script type="text/javascript">'
                '    zeit.cms.configure_ressort_dropdown("%s.");'
                '</script>') % (self.prefix,)
        return result


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


class TeaserText(InlineForm):

    legend = _('')
    prefix = 'teaser-text'
    undo_description = _('edit teaser text')

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata,
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
            'teaserText')
    form_fields['teaserText'].custom_widget = LimitedInputWidget

    def render(self):
        result = super(TeaserText, self).render()
        if result:
            result += (
                '<script type="text/javascript">'
                '    zeit.cms.configure_ressort_dropdown("%s.");'
                '</script>') % (self.prefix,)
        return result


class WorkflowForms(object):
    """Article workflow forms."""

    title = _('Workflow')


class WorkflowStatus(InlineForm):

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


class WorkflowSettings(InlineForm):

    legend = _('Settings')
    prefix = 'workflow-settings'
    undo_description = _('edit workflow settings')

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.workflow.interfaces.IContentWorkflow,
            zeit.content.article.interfaces.ICDSWorkflow,
            render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
                'release_period', 'urgent', 'export_cds'))


class WorkflowLog(InlineForm):

    legend = _('Log')
    prefix = 'workflow-log'
    undo_description = None

    form_fields = zope.formlib.form.FormFields(
            zeit.objectlog.interfaces.ILog,
            render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE)
