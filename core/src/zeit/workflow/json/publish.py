# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import cjson
import zeit.workflow.interfaces


class Publish(object):

    def publish(self):
        return cjson.encode(self._publish(self.context))

    def can_publish(self):
        return cjson.encode(self._can_publish(self.context))

    def _publish(self, content):
        if not self._can_publish(content):
            return False
        publish = zeit.cms.workflow.interfaces.IPublish(content)
        return publish.publish()

    def _can_publish(self, content):
        info = zeit.cms.workflow.interfaces.IPublishInfo(content)
        return info.can_publish()
