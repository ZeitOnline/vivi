from zeit.cms.workflow.interfaces import CAN_PUBLISH_ERROR
from zeit.cms.workflow.interfaces import CAN_PUBLISH_SUCCESS
import json
import zeit.cms.workflow.interfaces


class Publish(object):

    def publish(self):
        return json.dumps(self._publish())

    def can_publish(self):
        if self.publish_info.can_publish() == CAN_PUBLISH_SUCCESS:
            return json.dumps(True)
        return json.dumps(False)

    def retract(self):
        return json.dumps(self._retract())

    @property
    def publish_info(self):
        return zeit.cms.workflow.interfaces.IPublishInfo(self.context)

    def _publish(self):
        if self.publish_info.can_publish() == CAN_PUBLISH_ERROR:
            return False
        publish = zeit.cms.workflow.interfaces.IPublish(self.context)
        return publish.publish().id

    def _retract(self):
        publish = zeit.cms.workflow.interfaces.IPublish(self.context)
        return publish.retract().id
