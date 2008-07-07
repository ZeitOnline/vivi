# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.component
import zope.cachedescriptors.property

import zope.app.publisher.xmlrpc

import zeit.cms.repository.interfaces
import zeit.workflow.interfaces


class Publish(zope.app.publisher.xmlrpc.XMLRPCView):

    def can_publish(self, unique_id):
        info = zeit.cms.workflow.interfaces.IPublishInfo(
            self.repository.getContent(unique_id))
        return info.can_publish()

    def publish(self, unique_id):
        if not self.can_publish(unique_id):
            return False
        publish = zeit.cms.workflow.interfaces.IPublish(
            self.repository.getContent(unique_id))
        publish.publish()
        return True


    @zope.cachedescriptors.property.Lazy
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

