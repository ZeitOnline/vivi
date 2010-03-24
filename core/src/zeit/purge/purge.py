# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component
import httplib
import zeit.cms.repository.interfaces
import zeit.purge.interfaces
import zope.app.appsetup.product


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
            http = httplib.HTTPConnection(server, timeout=timeout)
            http.request('PURGE', url)
            response = http.getresponse()
            response.read()
            if response.status != 200:
                raise httplib.HTTPException(
                    "Server %s returned status %s (%s)" % (
                        server, response.status, response.reason))
