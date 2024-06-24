import csv
import logging
import random
import xmlrpc.client

import BTrees.Length
import grokcore.component as grok
import persistent
import zc.queue
import zope.app.appsetup.product
import zope.component
import zope.container.contained
import zope.interface
import zope.lifecycleevent
import zope.security.proxy

from zeit.cms.content.interfaces import WRITEABLE_LIVE
from zeit.vgwort.connection import in_daily_maintenance_window
import zeit.cms.cli
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.workflow.interfaces
import zeit.vgwort.interfaces


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.vgwort.interfaces.ITokens)
class TokenStorage(persistent.Persistent, zope.container.contained.Contained):
    def __init__(self):
        self._data = zc.queue.CompositeQueue(compositeSize=100)
        self._len = BTrees.Length.Length()

    def load(self, csv_file):
        reader = csv.reader(csv_file, delimiter=';')
        next(reader)  # skip first line
        for public_token, private_token in reader:
            self.add(public_token, private_token)

    def add(self, public_token, private_token):
        self._data.put((public_token, private_token))
        self._len.change(1)

    def claim(self):
        if len(self) == 0:
            raise ValueError('No tokens available.')
        value = self._data.pull(int(random.random() * (len(self) - 1)))
        self._len.change(-1)
        return value

    def claim_immediately(self):
        service = zope.component.getUtility(ITokenService)
        return service.claim_token()

    def order(self, amount):
        service = zope.component.getUtility(zeit.vgwort.interfaces.IPixelService)
        for public, private in service.order_pixels(amount):
            self.add(public, private)

    def __len__(self):
        return self._len()


class ITokenService(zope.interface.Interface):
    pass


@grok.implementer(ITokenService)
class TokenService(grok.GlobalUtility):
    """DAV does not support transactions, so we need to work around the case
    that an error occurs (and the transaction is rolled back) after a token has
    been claimed -- because the token has be written to DAV nonetheless, thus
    leading to duplicates.

    The solution is to make the act of claiming a token effective immediately,
    too, regardless of the transaction, just like DAV. We do this by moving the
    token claming to an XML-RPC call (which happens in its own, independent
    transaction).
    """

    def __init__(self):
        if not self.config:
            log.warning('No configuration found. Could not set up token service.')

    @property
    def config(self):
        return zope.app.appsetup.product.getProductConfiguration('zeit.vgwort')

    # Make mutable by tests.
    ServerProxy = xmlrpc.client.ServerProxy

    def claim_token(self):
        tokens = self.ServerProxy(self.config['claim-token-url'])
        return tokens.claim()


class Token(zeit.cms.content.dav.DAVPropertiesAdapter):
    grok.provides(zeit.vgwort.interfaces.IToken)

    zeit.cms.content.dav.mapProperties(
        zeit.vgwort.interfaces.IToken,
        'http://namespaces.zeit.de/CMS/vgwort',
        ('public_token', 'private_token'),
        writeable=WRITEABLE_LIVE,
    )


@grok.subscribe(
    zeit.vgwort.interfaces.IGenerallyReportableContent,
    zeit.cms.workflow.interfaces.IBeforePublishEvent,
)
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

    class Dummy:
        tzinfo = 'none'

        def isoformat(self):
            return ''

    never = Dummy()
    reginfo = zeit.vgwort.interfaces.IReportInfo(context)
    reginfo.reported_on = never
    reginfo.reported_error = ''


@grok.subscribe(zeit.cms.content.interfaces.ISynchronisingDAVPropertyToXMLEvent)
def ignore_private_token(event):
    if event.namespace == 'http://namespaces.zeit.de/CMS/vgwort' and event.name != 'public_token':
        event.veto()


@grok.subscribe(zeit.cms.interfaces.ICMSContent, zope.lifecycleevent.IObjectCopiedEvent)
def remove_vgwort_properties_after_copy(context, event):
    # This is internals; users may not edit token and report properties anyway.
    context = zope.security.proxy.removeSecurityProxy(context)
    token = zeit.vgwort.interfaces.IToken(context)
    token.public_token = None
    token.private_token = None
    info = zeit.vgwort.interfaces.IReportInfo(context)
    info.reported_on = None
    info.reported_error = None


@zeit.cms.cli.runner(principal=zeit.cms.cli.from_config('zeit.vgwort', 'token-principal'))
def order_tokens():
    if in_daily_maintenance_window():
        log.info('Skip inside daily VG-Wort API maintenance window')
        return

    _order_tokens()


def _order_tokens():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.vgwort')
    ts = zope.component.getUtility(zeit.vgwort.interfaces.ITokens)
    if len(ts) < int(config['minimum-token-amount']):
        ts.order(int(config['order-token-amount']))
