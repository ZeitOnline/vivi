# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing
import zeit.solr.testing
import zope.testing.doctest


ZCMLLayer = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=(
        zeit.cms.testing.cms_product_config +
        zeit.solr.testing.product_config))

class Layer(ZCMLLayer,
            zeit.solr.testing.SolrMockLayerBase):

    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def testSetUp(cls):
        pass

    @classmethod
    def testTearDown(cls):
        pass


class TestCase(zeit.cms.testing.FunctionalTestCase):

    layer = Layer


def FunctionalDocFileSuite(*args, **kw):
    kw.setdefault('layer', Layer)
    kw['package'] = zope.testing.doctest._normalize_module(kw.get('package'))
    return zeit.cms.testing.FunctionalDocFileSuite(*args, **kw)
