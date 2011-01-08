# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import socket
import grokcore.component
import httplib
import logging
import zeit.cms.repository.interfaces
import zeit.purge.interfaces
import zope.app.appsetup.product


log = logging.getLogger(__name__)


class Purge(grokcore.component.Adapter):

    grokcore.component.implements(zeit.purge.interfaces.IPurge)
    grokcore.component.context(
        zeit.cms.repository.interfaces.IRepositoryContent)

    def purge(self):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.purge')
        servers = config['servers'].split()
        public_prefix = config['public-prefix']
        timeout = int(config['purge-timeout'])
        url = self.context.uniqueId.replace(
            zeit.cms.interfaces.ID_NAMESPACE, public_prefix, 1)
        for server in servers:
            log.info("Purging %s on %s", url, server)
            http = httplib.HTTPConnection(server, timeout=timeout)
            try:
                http.request('PURGE', url)
                response = http.getresponse()
                response.read()
            except socket.error, e:
                raise zeit.purge.interfaces.PurgeError(server, e)
            if response.status != 200:
                raise zeit.purge.interfaces.PurgeError(
                    server, "Got status %s (%s)" % (
                        response.status, response.reason))
