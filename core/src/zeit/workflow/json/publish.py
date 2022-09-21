from zeit.cms.workflow.interfaces import CAN_PUBLISH_ERROR
from zeit.cms.workflow.interfaces import CAN_PUBLISH_SUCCESS
from zope.cachedescriptors.property import Lazy as cachedproperty
import json
import zeit.cms.workflow.interfaces
import zope.i18n


class Publish:

    def publish(self):
        return json.dumps(self._publish())

    def can_publish(self):
        if self.publish_info.can_publish() == CAN_PUBLISH_SUCCESS:
            return json.dumps(True)
        return json.dumps(False)

    def retract(self):
        return json.dumps(self._retract())

    @cachedproperty
    def publish_info(self):
        return zeit.cms.workflow.interfaces.IPublishInfo(self.context)

    def _publish(self):
        if self.publish_info.can_publish() == CAN_PUBLISH_ERROR:
            return {'error': ', '.join([
                zope.i18n.translate(x, context=self.request)
                for x in self.publish_info.error_messages])}
        publish = zeit.cms.workflow.interfaces.IPublish(self.context)
        result = publish.publish()
        if result is None:
            # ran inline instead of in background using celery tasks
            return
        return result.id

    def _retract(self):
        publish = zeit.cms.workflow.interfaces.IPublish(self.context)
        result = publish.retract()
        if result is None:
            # ran inline instead of in background using celery tasks
            return
        return result.id
