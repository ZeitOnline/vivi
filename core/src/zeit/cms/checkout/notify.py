import zope.event
import zope.publisher.xmlrpc

import zeit.cms.content.interfaces
import zeit.cms.interfaces


class Notify(zope.publisher.xmlrpc.XMLRPCView):
    def principal(self):
        return False

    def notify(self, unique_id):
        content = zeit.cms.interfaces.ICMSContent(unique_id)
        zope.event.notify(zeit.cms.content.interfaces.ContentModifiedEvent(content, self.principal))
