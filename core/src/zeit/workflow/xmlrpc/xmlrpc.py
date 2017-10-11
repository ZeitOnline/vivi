import zeit.cms.repository.interfaces
import zeit.workflow.interfaces
import zope.app.publisher.xmlrpc
import zope.cachedescriptors.property
import zope.component


class Publish(zope.app.publisher.xmlrpc.XMLRPCView):

    def can_publish(self, unique_id):
        info = zeit.cms.workflow.interfaces.IPublishInfo(
            self.repository.getContent(unique_id))
        can_publish = info.can_publish()

        if can_publish == zeit.cms.workflow.interfaces.CAN_PUBLISH_SUCCESS:
            return True
        return False

    def publish(self, unique_id):
        if not self.can_publish(unique_id):
            return False
        publish = zeit.cms.workflow.interfaces.IPublish(
            self.repository.getContent(unique_id))
        return publish.publish().id

    def retract(self, unique_id):
        publish = zeit.cms.workflow.interfaces.IPublish(
            self.repository.getContent(unique_id))
        return publish.retract().id

    @zope.cachedescriptors.property.Lazy
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
