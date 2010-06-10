# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing
import zope.testing.doctest


product_config = """
<product-config zeit.vgwort>
    vgwort-url https://tomtest.vgwort.de/
    username zeitonl
    password zeitabo2010
    minimum-token-amount 10
    order-token-amount 1
</product-config>
"""


ZCMLLayer = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml', product_config=product_config)


SOAPLayer = zeit.cms.testing.ZCMLLayer(
    'ftesting-soap.zcml', product_config=product_config)


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

    def new_document(self, content):
        pass # nyi
