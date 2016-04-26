from zeit.cms.repository.interfaces import IRepositoryContent
from zeit.cms.workflow.interfaces import CAN_PUBLISH_ERROR
from zeit.cms.workflow.interfaces import CAN_PUBLISH_SUCCESS
from zeit.cms.workflow.interfaces import CAN_PUBLISH_WARNING
from zeit.cms.workflow.interfaces import PRIORITY_DEFAULT
from zope.cachedescriptors.property import Lazy as cachedproperty
import lovely.remotetask.interfaces
import zeit.cms.browser.menu
import zeit.cms.workflow.interfaces
import zope.browserpage
import zope.component


class PublishMenuItem(zeit.cms.browser.menu.LightboxActionMenuItem):

    sort = -1
    lightbox = '@@publish.html'

    def render(self):
        return super(PublishMenuItem, self).render()


class Publish(object):
    """View for 1-Click-Publishing. Optionally displays validation info."""

    @cachedproperty
    def publish_info(self):
        return zeit.cms.workflow.interfaces.IPublishInfo(self.context)

    @property
    def can_override_publish_errors(self):
        return self.publish_info.can_publish() == CAN_PUBLISH_WARNING

    @property
    def error_messages(self):
        return self.publish_info.error_messages

    def render_error_messages(self):
        return zope.browserpage.ViewPageTemplateFile('publish-errors.pt')(self)

    def can_publish(self):
        """Allow publish when validation warnings are present."""
        result = self.publish_info.can_publish()
        if result == CAN_PUBLISH_SUCCESS:
            return True
        if result == CAN_PUBLISH_ERROR:
            return False
        return 'force' in self.request.form  # Override CAN_PUBLISH_WARNING


class FlashPublishErrors(zeit.cms.browser.view.Base):

    def __call__(self, job):
        job = int(job)
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        priority = zeit.cms.workflow.interfaces.IPublishPriority(self.context)
        queue = config['task-queue-%s' % priority]
        tasks = zope.component.getUtility(
            lovely.remotetask.interfaces.ITaskService, name=queue)
        if tasks.getStatus(job) != lovely.remotetask.interfaces.COMPLETED:
            return
        error = tasks.getResult(job)
        if error is not None:
            self.send_message(error, type='error')


class RetractMenuItem(zeit.cms.browser.menu.LightboxActionMenuItem):

    sort = 200
    lightbox = '@@retract.html'

    @property
    def visible(self):
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.context)
        return info.published

    def render(self):
        if not self.visible or not IRepositoryContent.providedBy(self.context):
            return ''
        else:
            return super(RetractMenuItem, self).render()
