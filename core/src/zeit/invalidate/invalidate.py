
import logging
import six
import six.moves.xmlrpc_client
import zeit.connector.interfaces
import zope.app.publisher.xmlrpc
import zope.event


logger = logging.getLogger(__name__)


class Invalidate(zope.app.publisher.xmlrpc.XMLRPCView):

    def invalidate(self, resource_id):
        if not isinstance(resource_id, six.string_types):
            raise six.moves.xmlrpc_client.Fault(
                100, "`resource_id` must be string type, got %s" % (
                    type(resource_id)))
        self._do_invalidate(resource_id)
        return True

    def invalidate_many(self, resource_list):
        if not isinstance(resource_list, (list, tuple)):
            raise six.moves.xmlrpc_client.Fault(
                100, "`resource_list` must be sequence type, got %s" % (
                    type(resource_list)))

        for resource_id in resource_list:
            self._do_invalidate(resource_id)
        return True

    def _do_invalidate(self, resource_id):
        logger.info('%s invalidated %s.' % (self.request.principal.id,
                                            resource_id))
        zope.event.notify(
            zeit.connector.interfaces.ResourceInvaliatedEvent(resource_id))
