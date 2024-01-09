import json

from zope.cachedescriptors.property import Lazy as cachedproperty
import zope.i18n

from zeit.cms.workflow.interfaces import (
    CAN_PUBLISH_ERROR,
    CAN_PUBLISH_SUCCESS,
    CAN_RETRACT_ERROR,
    CAN_RETRACT_SUCCESS,
)
import zeit.cms.workflow.interfaces


class Publish:
    def publish(self):
        return json.dumps(self._publish())

    def can_publish(self):
        if self.publish_info.can_publish() == CAN_PUBLISH_SUCCESS:
            return json.dumps(True)
        return json.dumps(False)

    def can_retract(self):
        if self.publish_info.can_retract() == CAN_RETRACT_SUCCESS:
            return json.dumps(True)
        return json.dumps(False)

    def retract(self):
        return json.dumps(self._retract())

    @cachedproperty
    def publish_info(self):
        return zeit.cms.workflow.interfaces.IPublishInfo(self.context)

    def _publish(self):
        if self.publish_info.can_publish() == CAN_PUBLISH_ERROR:
            return {
                'error': ', '.join(
                    [
                        zope.i18n.translate(x, context=self.request)
                        for x in self.publish_info.error_messages
                    ]
                )
            }
        publish = zeit.cms.workflow.interfaces.IPublish(self.context)
        return publish.publish().id

    def _retract(self):
        if self.publish_info.can_retract() == CAN_RETRACT_ERROR:
            return {
                'error': ', '.join(
                    [
                        zope.i18n.translate(x, context=self.request)
                        for x in self.publish_info.error_messages
                    ]
                )
            }
        publish = zeit.cms.workflow.interfaces.IPublish(self.context)
        return publish.retract().id
