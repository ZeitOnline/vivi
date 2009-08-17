# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import cjson
import zeit.workflow.interfaces


class Publish(object):

    def __call__(self):
        return cjson.encode(self.publish(self.context))

    def publish(self, content):
        if not self.can_publish(content):
            return False
        publish = zeit.cms.workflow.interfaces.IPublish(content)
        return publish.publish()

    def can_publish(self, content):
        info = zeit.cms.workflow.interfaces.IPublishInfo(content)
        return info.can_publish()
