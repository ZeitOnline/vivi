# Copyright (c) 2010-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
from zope.cachedescriptors.property import Lazy as cachedproperty
import zeit.cms.browser.view
import zeit.content.article.interfaces
import zeit.edit.browser.form
import zeit.workflow.interfaces
import zope.formlib.form
import zope.formlib.interfaces
import zope.i18n


class WorkflowContainer(zeit.edit.browser.form.FormGroup):
    """Article workflow forms."""


class Urgent(zeit.edit.browser.form.InlineForm):

    legend = _('')
    prefix = 'urgent'
    undo_description = _('edit urgent')

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.workflow.interfaces.IContentWorkflow,
            render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
                'urgent'))


class Checkin(zeit.cms.browser.view.Base):

    @cachedproperty
    def checkin_manager(self):
        return zeit.cms.checkout.interfaces.ICheckinManager(self.context)

    @cachedproperty
    def can_checkin(self):
        return self.checkin_manager.canCheckin

    @cachedproperty
    def checkin_errors(self):
        self.can_checkin # cause last_validation_error to be populated
        if not self.checkin_manager.last_validation_error:
            return []

        result = []
        for name, error in self.checkin_manager.last_validation_error:
            # adapted from zope.formlib.form.FormBase.error_views
            view = zope.component.getMultiAdapter(
                (error, self.request),
                zope.formlib.interfaces.IWidgetInputErrorView)
            title = zeit.content.article.interfaces.IArticle[name].title
            if isinstance(title, zope.i18n.Message):
                title = zope.i18n.translate(title, context=self.request)
            result.append(dict(name=title, snippet=view.snippet()))
        return result

    @property
    def checkin_url(self):
        return self.url(name='@@checkin')

    @cachedproperty
    def can_checkout(self):
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(self.context)
        return manager.canCheckout

    @cachedproperty
    def published(self):
        publish_info = zeit.cms.workflow.interfaces.IPublishInfo(self.context)
        return publish_info.published

    def __call__(self, semantic_change=False):
        if self.request.method != 'POST':
            return super(Checkin, self).__call__()
        checkin = zope.component.getMultiAdapter(
            (self.context, self.request),
            zope.interface.Interface,
            name='checkin')
        return checkin(semantic_change=(semantic_change == 'true'))
