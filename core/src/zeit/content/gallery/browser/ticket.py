# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt
"""Ticket authentication."""

import base64
import hashlib
import random
import struct
import sys
import sys
import zope.app.appsetup.product
import zope.component
import zope.interface
import zope.publisher.interfaces.browser
import zope.security
import zope.traversing.interfaces


class TicketTraverser(object):
    """This traverser takes a ticket and authenticates the user.

    This is useful for uploading files with flash.

    """

    zope.component.adapts(
        zope.interface.Interface,
        zope.publisher.interfaces.browser.IDefaultBrowserLayer)

    zope.interface.implements(zope.traversing.interfaces.ITraversable)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, furtherPath):
        auth = zope.component.getUtility(
            zope.app.security.interfaces.IAuthentication)
        rnd, hash_, principal = unpack(name)
        if not get_hash(rnd, principal) == name:
            raise zope.security.interfaces.Unauthorized
        self.request.setPrincipal(auth.getPrincipal(principal))
        return self.context


class TicketIssuer(object):
    """Issue ticket for currently logged in user.

    A ticket allows to authenticate.

    """

    def __call__(self):
        principal = self.request.principal
        if zope.authentication.interfaces.IUnauthenticatedPrincipal.providedBy(
            principal):
            raise zope.security.interfaces.Unauthorized
        principal = principal.id
        rnd = random.randint(-sys.maxint, sys.maxint)
        self.request.response.setHeader('Content-Type', 'text/plain')
        self.request.response.setHeader('Cache-Control', 'no-cache')
        ticket = get_hash(rnd, principal)
        return ticket


def get_hash(rnd, principal):
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.content.gallery')
    secret = config['ticket-secret']
    ticket_hash = hashlib.sha224()

    for element in (secret, str(rnd), principal):
        ticket_hash.update(element)
    hash_ = ticket_hash.digest()
    return pack(rnd, hash_, principal)


format = '>i28s'

def pack(rnd, hash_, principal):
    packed = struct.pack(format, rnd, hash_) + principal
    return base64.urlsafe_b64encode(packed).strip()

def unpack(ticket):
    ticket = base64.urlsafe_b64decode(str(ticket))
    rnd, hash_ = struct.unpack_from(format, ticket)
    principal = ticket[struct.calcsize(format):]
    return rnd, hash_, principal
