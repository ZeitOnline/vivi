# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.vgwort.interfaces
import zope.component
import zope.publisher.xmlrpc


class AvailableTokens(object):

    def __call__(self):
        tokens = zope.component.getUtility(zeit.vgwort.interfaces.ITokens)
        return str(len(tokens))


class TokenStorage(zope.publisher.xmlrpc.XMLRPCView):

    def claim(self):
        tokens = zope.component.getUtility(zeit.vgwort.interfaces.ITokens)
        return tokens.claim()
