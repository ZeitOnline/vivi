import logging
import xmlrpc.client

import zope.event
import zope.publisher.xmlrpc

import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.connector.interfaces


log = logging.getLogger(__name__)


class Notify(zope.publisher.xmlrpc.XMLRPCView):
    def principal(self):
        return False

    def notify(self, resource_id):
        if not isinstance(resource_id, str):
            raise xmlrpc.client.Fault(
                100, '`resource_id` must be string type, got %s' % (type(resource_id))
            )
        self._notify(resource_id)

    def _notify(self, resource_id):
        log.info('%s content modified %s.' % (self.request.principal.id, resource_id))
        zope.event.notify(zeit.connector.interfaces.ResourceInvalidatedEvent(resource_id))
        content = zeit.cms.interfaces.ICMSContent(resource_id)
        zope.event.notify(zeit.cms.content.interfaces.ContentModifiedEvent(content, self.principal))
