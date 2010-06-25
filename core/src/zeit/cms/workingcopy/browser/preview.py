# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.content.interfaces
import zeit.preview.interfaces
import zope.component
import zope.security.proxy


class WorkingcopyPreview(object):

    def __call__(self):
        preview = zope.component.getUtility(zeit.preview.interfaces.IPreview)
        xmlrep = zeit.cms.content.interfaces.IXMLRepresentation(
            zope.security.proxy.removeSecurityProxy(self.context))
        return preview.transform(
            xmlrep.xml,
            params=self.request.environment['QUERY_STRING'])
