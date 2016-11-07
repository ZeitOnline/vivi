from zeit.cms.content.interfaces import WRITEABLE_LIVE
import BTrees.Length
import csv
import gocept.runner
import grokcore.component
import logging
import persistent
import random
import xmlrpclib
import zc.queue
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.workflow.interfaces
import zeit.vgwort.interfaces
import zope.app.appsetup.product
import zope.component
import zope.container.contained
import zope.interface
import zope.lifecycleevent
import zope.security.proxy


log = logging.getLogger(__name__)


class TokenStorage(persistent.Persistent,
                   zope.container.contained.Contained):

    zope.interface.implements(zeit.vgwort.interfaces.ITokens)

    def __init__(self):
        self._data = zc.queue.CompositeQueue(compositeSize=100)
        self._len = BTrees.Length.Length()

    def load(self, csv_file):
        reader = csv.reader(csv_file, delimiter=';')
        reader.next()  # skip first line
        for public_token, private_token in reader:
            self.add(public_token, private_token)

    def add(self, public_token, private_token):
        self._data.put((public_token, private_token))
        self._len.change(1)

    def claim(self):
        if len(self) == 0:
            raise ValueError("No tokens available.")
        value = self._data.pull(random.randint(0, len(self) - 1))
        self._len.change(-1)
        return value

    def claim_immediately(self):
        service = zope.component.getUtility(ITokenService)
        return service.claim_token()

    def order(self, amount):
        service = zope.component.getUtility(
            zeit.vgwort.interfaces.IPixelService)
        for public, private in service.order_pixels(amount):
            self.add(public, private)

    def __len__(self):
        return self._len()


class ITokenService(zope.interface.Interface):
    pass


class TokenService(grokcore.component.GlobalUtility):
    """DAV does not support transactions, so we need to work around the case
    that an error occurs (and the transaction is rolled back) after a token has
    been claimed -- because the token has be written to DAV nonetheless, thus
    leading to duplicates.

    The solution is to make the act of claiming a token effective immediately,
    too, regardless of the transaction, just like DAV. We do this by moving the
    token claming to an XML-RPC call (which happens in its own, independent
    transaction).
    """

    grokcore.component.implements(ITokenService)

    def __init__(self):
        if not self.config:
            log.warning(
                'No configuration found. Could not set up token service.')

    @property
    def config(self):
        return zope.app.appsetup.product.getProductConfiguration('zeit.vgwort')

    # Make mutable by tests.
    ServerProxy = xmlrpclib.ServerProxy

    def claim_token(self):
        tokens = self.ServerProxy(self.config['claim-token-url'])
        return tokens.claim()


class Token(zeit.cms.content.dav.DAVPropertiesAdapter):

    grokcore.component.provides(zeit.vgwort.interfaces.IToken)

    zeit.cms.content.dav.mapProperties(
        zeit.vgwort.interfaces.IToken,
        'http://namespaces.zeit.de/CMS/vgwort',
        ('public_token', 'private_token'),
        writeable=WRITEABLE_LIVE)


@grokcore.component.subscribe(
    zeit.vgwort.interfaces.IGenerallyReportableContent,
    zeit.cms.workflow.interfaces.IBeforePublishEvent)
def add_token(context, event):
    if context != event.master:
        # Only assign tokens to the master
        return

    token = zeit.vgwort.interfaces.IToken(context)
    if token.public_token:
        # Already has a token. Do nothing then.
        return

    tokens = zope.component.getUtility(zeit.vgwort.interfaces.ITokens)
    token.public_token, token.private_token = tokens.claim_immediately()

    class Dummy(object):
        tzinfo = 'none'

        def isoformat(self):
            return ''
    never = Dummy()
    reginfo = zeit.vgwort.interfaces.IReportInfo(context)
    reginfo.reported_on = never
    reginfo.reported_error = ''


@grokcore.component.subscribe(
    zeit.cms.content.interfaces.ISynchronisingDAVPropertyToXMLEvent)
def ignore_private_token(event):
    if (event.namespace == 'http://namespaces.zeit.de/CMS/vgwort' and
            event.name != 'public_token'):
        event.veto()


@grokcore.component.subscribe(
    zeit.cms.interfaces.ICMSContent,
    zope.lifecycleevent.IObjectCopiedEvent)
def remove_vgwort_properties_after_copy(context, event):
    # This is internals; users may not edit token and report properties anyway.
    context = zope.security.proxy.removeSecurityProxy(context)
    token = zeit.vgwort.interfaces.IToken(context)
    token.public_token = None
    token.private_token = None
    info = zeit.vgwort.interfaces.IReportInfo(context)
    info.reported_on = None
    info.reported_error = None


@gocept.runner.once(principal=gocept.runner.from_config(
    'zeit.vgwort', 'token-principal'))
def order_tokens():
    _order_tokens()


def _order_tokens():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.vgwort')
    ts = zope.component.getUtility(
        zeit.vgwort.interfaces.ITokens)
    if len(ts) < int(config['minimum-token-amount']):
        ts.order(int(config['order-token-amount']))
