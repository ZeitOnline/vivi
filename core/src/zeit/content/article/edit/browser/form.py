# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.asset.browser
import zeit.cms.browser.interfaces
import zeit.content.article.interfaces
import zeit.edit.browser.form
import zope.formlib.form
import zope.formlib.interfaces
import zope.interface


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
    prefix = 'worfklow-settings'
    undo_description = _('edit workflow settings')

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.workflow.interfaces.IContentWorkflow,
            zeit.content.article.interfaces.ICDSWorkflow,
            render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
                'release_period', 'urgent', 'export_cds'))


class WorkflowLog(zeit.edit.browser.form.InlineForm):

    legend = _('Log')
    prefix = 'worfklow-log'
    undo_description = None

    form_fields = zope.formlib.form.FormFields(
            zeit.objectlog.interfaces.ILog,
            render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE)
