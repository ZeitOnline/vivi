import base64
import hashlib
import random
import struct
import sys

import zope.component
import zope.interface
import zope.publisher.interfaces.browser
import zope.security
import zope.traversing.interfaces

import zeit.cms.config


@zope.component.adapter(
    zope.interface.Interface, zope.publisher.interfaces.browser.IDefaultBrowserLayer
)
@zope.interface.implementer(zope.traversing.interfaces.ITraversable)
class TicketTraverser:
    """This traverser takes a ticket and authenticates the user.

    This is useful for uploading files with flash.

    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, furtherPath):
        auth = zope.component.getUtility(zope.app.security.interfaces.IAuthentication)
        rnd, hash_, principal = unpack(name)
        if not get_hash(rnd, principal) == name:
            raise zope.security.interfaces.Unauthorized
        self.request.setPrincipal(auth.getPrincipal(principal))
        return self.context


class TicketIssuer:
    """Issue ticket for currently logged in user.

    A ticket allows to authenticate.

    """

    def __call__(self):
        principal = self.request.principal
        if zope.authentication.interfaces.IUnauthenticatedPrincipal.providedBy(principal):
            raise zope.security.interfaces.Unauthorized
        rnd = random.randint(-sys.maxsize, sys.maxsize)
        self.request.response.setHeader('Content-Type', 'text/plain')
        self.request.response.setHeader('Cache-Control', 'no-cache')
        ticket = get_hash(rnd, principal.id)
        return ticket


def get_hash(rnd, principal):
    secret = zeit.cms.config.required('zeit.content.gallery', 'ticket-secret')
    ticket_hash = hashlib.sha224()

    for element in (secret, str(rnd), principal):
        ticket_hash.update(element.encode('utf-8'))
    hash_ = ticket_hash.digest()
    return pack(rnd, hash_, principal)


format = '>q28s'


def pack(rnd, hash_, principal):
    packed = struct.pack(format, rnd, hash_) + principal.encode('utf-8')
    return base64.urlsafe_b64encode(packed).decode('ascii').strip()


def unpack(ticket):
    ticket = base64.urlsafe_b64decode(ticket.encode('ascii'))
    rnd, hash_ = struct.unpack_from(format, ticket)
    principal = ticket[struct.calcsize(format) :].decode('utf-8')
    return rnd, hash_, principal
