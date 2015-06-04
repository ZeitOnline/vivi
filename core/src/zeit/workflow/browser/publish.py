from zeit.cms.repository.interfaces import IRepositoryContent
from zope.cachedescriptors.property import Lazy as cachedproperty
import lovely.remotetask.interfaces
import zeit.cms.browser.menu
import zeit.cms.workflow.interfaces
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

    @cachedproperty
    def validation_info(self):
        """Avoid execution of validation twice by reusing publish_info.

        IPublishInfo and IPublishValidationInfo are implemented by the same
        object, thus calling the adapter IPublishValidationInfo will not
        calculate the validations twice, since the Workflow already implements
        the interface.

        """
        return zeit.cms.workflow.interfaces.IPublishValidationInfo(
            self.publish_info, None)

    @property
    def validation_status(self):
        if self.validation_info is None:
            return None
        return self.validation_info.status

    @property
    def validation_messages(self):
        if self.validation_info is None:
            return None
        return set(self.validation_info.messages)

    @property
    def has_validation_error(self):
        return self.validation_status == 'error'

    def can_publish(self):
        """Allow publish when validation warnings are present.

        a) When no validation issue is present, allow publishing.
        b) If validation *errors* are present, publishing is denied.
        c) If validation *warnings* are present,
           publishing is allowed when the force argument is given.

        """
        if not self.publish_info.can_publish():
            return False
        if self.validation_status is None:
            return True
        if self.has_validation_error:
            return False
        return 'force' in self.request.form


class FlashPublishErrors(zeit.cms.browser.view.Base):

    def __call__(self, job):
        job = int(job)
        tasks = zope.component.getUtility(
            lovely.remotetask.interfaces.ITaskService, name='general')
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
