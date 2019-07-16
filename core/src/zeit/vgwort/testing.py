import os
import pytest
import unittest
import zeit.cms.content.interfaces
import zeit.cms.testing
import zeit.vgwort.interfaces
import zope.app.testing.xmlrpc
import zope.component
import zope.index.text.interfaces
import zope.interface


product_config = """
<product-config zeit.vgwort>
    vgwort-url https://tom-test.vgwort.de/
    username {username}
    password {password}
    minimum-token-amount 10
    order-token-amount 1
    days-before-report 7
    claim-token-url http://user:userpw@localhost/
</product-config>
""".format(
    username=os.environ.get('ZEIT_VGWORT_USERNAME'),
    password=os.environ.get('ZEIT_VGWORT_PASSWORD'),
)


class ZCMLLayer(zeit.cms.testing.ZCMLLayer):

    def setUp(self):
        super(ZCMLLayer, self).setUp()
        token_service = zeit.vgwort.token.TokenService()
        token_service.ServerProxy = zope.app.testing.xmlrpc.ServerProxy
        zope.component.getSiteManager().registerUtility(token_service)


ZCML_LAYER = ZCMLLayer(
    'ftesting-mock.zcml',
    product_config=zeit.cms.testing.cms_product_config + product_config)

WSGI_LAYER = zeit.cms.testing.WSGILayer(name='WSGILayer', bases=(ZCML_LAYER,))

SOAPLayer = zeit.cms.testing.ZCMLLayer(
    'ftesting-soap.zcml', name='SOAPLayer',
    product_config=zeit.cms.testing.cms_product_config + product_config)


class TestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZCML_LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):

    layer = WSGI_LAYER


@pytest.mark.slow
class EndToEndTestCase(zeit.cms.testing.FunctionalTestCase,
                       unittest.TestCase):

    layer = SOAPLayer
    level = 2

    def setUp(self):
        super(EndToEndTestCase, self).setUp()
        service = zope.component.getUtility(
            zeit.vgwort.interfaces.IMessageService)
        try:
            service.call('qualityControl')
        except:
            self.skipTest('vgwort test system is down')


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
