import logging
import xmlrpc.client

import zope.event
import zope.publisher.xmlrpc

import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.connector.interfaces


log = logging.getLogger(__name__)


class ContentModified(zope.publisher.xmlrpc.XMLRPCView):
    def content_modified(self, resource_id):
        if not isinstance(resource_id, str):
            raise xmlrpc.client.Fault(
                100, '`resource_id` must be string type, got %s' % (type(resource_id))
            )
        log.info('%s content modified %s.' % (self.request.principal.id, resource_id))
        zope.event.notify(zeit.connector.interfaces.ResourceInvalidatedEvent(resource_id))
        self._content_modified(resource_id)

    def _content_modified(self, resource_id):
        try:
            content = zeit.cms.interfaces.ICMSContent(resource_id)
        except TypeError:
            log.warning('%s does not exist anymore', resource_id)
            return

        zope.event.notify(
            zeit.cms.content.interfaces.ContentModifiedEvent(content, self.request.principal)
        )
        zope.event.notify(zeit.cms.checkout.interfaces.ContentIndexEvent(content))
