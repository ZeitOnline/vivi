# Copyright (c) 2010-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
from zeit.cms.repository.interfaces import IAutomaticallyRenameable
from zeit.workflow.interfaces import IReview
from zope.cachedescriptors.property import Lazy as cachedproperty
import zeit.cms.browser.view
import zeit.cms.checkout.browser.manager
import zeit.content.article.interfaces
import zeit.edit.browser.form
import zeit.workflow.interfaces
import zope.formlib.form
import zope.formlib.interfaces
import zope.i18n


class WorkflowContainer(zeit.edit.browser.form.FoldableFormGroup):
    """Article workflow forms."""

    title = _('Workflow')


class Publish(zeit.edit.browser.form.InlineForm,
              zeit.workflow.browser.form.WorkflowActions):

    legend = _('')
    prefix = 'publish'
    undo_description = _('edit workflow status')

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.workflow.interfaces.IReview))

    def setUpWidgets(self, *args, **kw):
        super(Publish, self).setUpWidgets(*args, **kw)
        if IReview(self.context).urgent:
            # XXX This needs a better mechanism.
            for name in ('corrected', 'edited'):
                self.widgets[name].extra = 'disabled="disabled"'
                self.widgets[name].vivi_css_class = 'disabled'

    @zope.formlib.form.action(_('Save & Publish'), name='publish')
    def handle_publish(self, action, data):
        # "super" call to apply changes
        self.handle_edit_action.success_handler(self, action, data)
        self.do_publish()


class ExportCDS(zeit.edit.browser.form.InlineForm,
                zeit.workflow.browser.form.WorkflowActions):

    legend = _('')
    prefix = 'export-cds'
    undo_description = _('edit export cds')

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.content.article.interfaces.ICDSWorkflow))


class SemanticChange(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'semantic-change'
    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ISemanticChange).select(
        'has_semantic_change')


class Checkin(zeit.cms.browser.view.Base,
              zeit.cms.checkout.browser.manager.CheckinAndRedirect):

    @cachedproperty
    def checkin_errors(self):
        self.canCheckin  # cause last_validation_error to be populated
        if (not self.manager.last_validation_error
            # XXX stopgap so it doesn't break, see #10851
            or not isinstance(
                self.manager.last_validation_error, list)):
            return []

        result = []
        for name, error in self.manager.last_validation_error:
            # adapted from zope.formlib.form.FormBase.error_views
            view = zope.component.getMultiAdapter(
                (error, self.request),
                zope.formlib.interfaces.IWidgetInputErrorView)
            title = zeit.content.article.interfaces.IArticle[name].title
            if isinstance(title, zope.i18n.Message):
                title = zope.i18n.translate(title, context=self.request)
            result.append(dict(name=title, snippet=view.snippet()))
        return result

    @cachedproperty
    def can_checkout(self):
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(self.context)
        return manager.canCheckout

    @cachedproperty
    def published(self):
        publish_info = zeit.cms.workflow.interfaces.IPublishInfo(self.context)
        return publish_info.published

    @property
    def is_new(self):
        return IAutomaticallyRenameable(self.context).renameable

    def __call__(self):
        if self.request.method == 'POST':
            return self.perform_checkin()
        else:
            return super(Checkin, self).__call__()
