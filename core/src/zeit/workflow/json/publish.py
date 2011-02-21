# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import cjson
import zeit.workflow.interfaces


class Publish(object):

    def publish(self):
        return cjson.encode(self._publish())

    def can_publish(self):
        return cjson.encode(self.publish_info.can_publish())

    def retract(self):
        return cjson.encode(self._retract())

    @property
    def publish_info(self):
        return zeit.cms.workflow.interfaces.IPublishInfo(self.context)

    def _publish(self):
        if not self.publish_info.can_publish():
            return False
        publish = zeit.cms.workflow.interfaces.IPublish(self.context)
        return publish.publish()

    def _retract(self):
        publish = zeit.cms.workflow.interfaces.IPublish(self.context)
        return publish.retract()
