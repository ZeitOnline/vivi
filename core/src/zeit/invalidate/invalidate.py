# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import logging
import xmlrpclib

import zope.event

import zope.app.publisher.xmlrpc

import zeit.connector.interfaces


logger = logging.getLogger(__name__)


class Invalidate(zope.app.publisher.xmlrpc.XMLRPCView):

    def invalidate(self, resource_id):
        if not isinstance(resource_id, basestring):
            raise xmlrpclib.Fault(
                100, "`resource_id` must be string type, got %s" % (
                    type(resource_id)))
        logger.info('%s invalidated %s.' % (self.request.principal.id,
                                            resource_id))
        zope.event.notify(
            zeit.connector.interfaces.ResourceInvaliatedEvent(resource_id))
