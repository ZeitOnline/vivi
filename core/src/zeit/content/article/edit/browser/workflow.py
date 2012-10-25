# Copyright (c) 2010-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
from zeit.cms.repository.interfaces import IAutomaticallyRenameable
from zeit.workflow.interfaces import IReview
from zope.cachedescriptors.property import Lazy as cachedproperty
import mock
import zeit.cms.browser.view
import zeit.cms.checkout.browser.manager
import zeit.content.article.interfaces
import zeit.edit.browser.form
import zeit.workflow.interfaces
import zope.component
import zope.formlib.form
import zope.formlib.interfaces
import zope.formlib.widget
import zope.i18n


class WorkflowContainer(zeit.edit.browser.form.FoldableFormGroup):
    """Article workflow forms."""

    title = _('Workflow')


class Publish(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'publish'
    undo_description = _('edit workflow status')

    @property
    def form_fields(self):
        fields = zope.formlib.form.FormFields(
            zeit.workflow.interfaces.IReview,
            zeit.content.article.interfaces.ICDSWorkflow)
        if not self.can_checkout:
            fields += zope.formlib.form.FormFields(
                zeit.cms.content.interfaces.ISemanticChange).select(
                'has_semantic_change')
        return fields

    def setUpWidgets(self, *args, **kw):
        super(Publish, self).setUpWidgets(*args, **kw)
        if IReview(self.context).urgent:
            # XXX This needs a better mechanism.
            for name in ('corrected', 'edited'):
                self.widgets[name].extra = 'disabled="disabled"'
                self.widgets[name].vivi_css_class = 'disabled'
        self.widgets['export_cds'].vivi_css_class = 'visual-clear'

        if not self.can_checkout:
            items = list(self.widgets.__Widgets_widgets_items__)
            for name in ('edit.form.checkin-errors', 'edit.form.timestamp'):
                widget = ViewWidget(self.context, self.request, name)
                widget.setPrefix(self.prefix)
                items.insert(-1, (None, widget))
            self.widgets = zope.formlib.form.Widgets(items, prefix=self.prefix)

    @cachedproperty
    def can_checkout(self):
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(self.context)
        return manager.canCheckout


class CheckinErrors(object):

    @cachedproperty
    def checkin_errors(self):
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(self.context)
        manager.canCheckin  # cause last_validation_error to be populated
        errors = manager.last_validation_error
        if (not errors
            # XXX stopgap so it doesn't break, see #10851
            or not isinstance(errors, list)):
            return []

        result = []
        for name, error in errors:
            # adapted from zope.formlib.form.FormBase.error_views
            view = zope.component.getMultiAdapter(
                (error, self.request),
                zope.formlib.interfaces.IWidgetInputErrorView)
            title = zeit.content.article.interfaces.IArticle[name].title
            if isinstance(title, zope.i18n.Message):
                title = zope.i18n.translate(title, context=self.request)
            result.append(dict(name=title, snippet=view.snippet()))
        return result


class WorkflowButtons(object):

    @cachedproperty
    def can_checkout(self):
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(self.context)
        return manager.canCheckout

    @cachedproperty
    def can_checkin(self):
        manager = zeit.cms.checkout.interfaces.ICheckinManager(self.context)
        return manager.canCheckin

    @cachedproperty
    def published(self):
        publish_info = zeit.cms.workflow.interfaces.IPublishInfo(self.context)
        return publish_info.published

    @property
    def is_new(self):
        return IAutomaticallyRenameable(self.context).renameable


class ViewWidget(zope.formlib.widget.BrowserWidget):

    field_css_class = ''

    def __init__(self, context, request, view):
        field = mock.Mock()
        field.__name__ = 'htmlcontent.%s' % id(self)
        super(ViewWidget, self).__init__(field, request)
        self.context = context
        self.request = request
        self.view = view
        self.label = None

    def __call__(self):
        view = zope.component.getMultiAdapter(
            (self.context, self.request), name=self.view)
        return view()
