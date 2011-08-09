# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import xmlrpclib
import zeit.cms.content.interfaces
import zeit.cms.testing
import zeit.vgwort.interfaces
import zope.app.testing.xmlrpc
import zope.component
import zope.index.text.interfaces
import zope.interface
import zope.testing.doctest


product_config = """
<product-config zeit.vgwort>
    vgwort-url https://tom-test.vgwort.de/
    username zeitonl
    password zeitabo2010
    minimum-token-amount 10
    order-token-amount 1
    days-before-report 7
    claim-token-url http://user:userpw@localhost/
</product-config>
"""


ZCMLLayerBase = zeit.cms.testing.ZCMLLayer(
    'ftesting-mock.zcml',
    product_config=zeit.cms.testing.cms_product_config + product_config)


SOAPLayer = zeit.cms.testing.ZCMLLayer(
    'ftesting-soap.zcml',
    product_config=zeit.cms.testing.cms_product_config + product_config)


class ZCMLLayer(ZCMLLayerBase):

    @classmethod
    def setUp(cls):
        # inject a testing xmlrpc ServerProxy into the TokenService
        # XXX ugly!
        def patch_once(*args, **kw):
            if cls.patch_called:
                cls.patcher.stop()
                return xmlrpclib.ServerProxy(*args, **kw)
            else:
                cls.patch_called = True
                return zope.app.testing.xmlrpc.ServerProxy(*args, **kw)

        cls.patcher = mock.patch('xmlrpclib.ServerProxy', patch_once)
        cls.patcher.start()
        cls.patch_called = False

        zope.component.getSiteManager().registerUtility(
            zeit.vgwort.token.TokenService())


def FunctionalDocFileSuite(*args, **kw):
    kw.setdefault('layer', ZCMLLayer)
    kw['package'] = zope.testing.doctest._normalize_module(kw.get('package'))
    return zeit.cms.testing.FunctionalDocFileSuite(*args, **kw)


class TestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZCMLLayer


class EndToEndTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = SOAPLayer
    level = 2


class PixelService(object):

    zope.interface.implements(zeit.vgwort.interfaces.IPixelService)

    def order_pixels(self, amount):
        for i in range(amount):
            yield ('public-%s' % i, 'private-%s' % i)


class MessageService(object):

    zope.interface.implements(zeit.vgwort.interfaces.IMessageService)

    def __init__(self):
        self.reset()

    def reset(self):
        self.calls = []
        self.error = None

    def new_document(self, content):
        if self.error:
            raise self.error('Provoked error')
        self.calls.append(content)


class SearchableText(object):

    zope.component.adapts(zeit.cms.content.interfaces.ICommonMetadata)
    zope.interface.implements(zope.index.text.interfaces.ISearchableText)

    def __init__(self, context):
        self.context = context

    def getSearchableText(self):
        return [self.context.teaserText or '']
