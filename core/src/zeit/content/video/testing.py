# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing
import zope.testing.doctest


Layer = zeit.cms.testing.ZCMLLayer('ftesting.zcml', product_config=True)


class TestCase(zeit.cms.testing.FunctionalTestCase):

    layer = Layer


def FunctionalDocFileSuite(*args, **kw):
    kw.setdefault('layer', Layer)
    kw['package'] = zope.testing.doctest._normalize_module(kw.get('package'))
    return zeit.cms.testing.FunctionalDocFileSuite(*args, **kw)
