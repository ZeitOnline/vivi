# Copyright (c) 2008-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.selenium.ztk
import pkg_resources
import zeit.cms.testing
import zeit.find.search


product_config = """\
<product-config zeit.solr>
    solr-url file://%s
    public-solr-url file://%s
</product-config>
""" % (pkg_resources.resource_filename(__name__, 'testdata'),
       pkg_resources.resource_filename(__name__, 'testdata'))


SearchLayer = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=zeit.cms.testing.cms_product_config + product_config)


SeleniumLayer = gocept.selenium.ztk.Layer(SearchLayer)


class QueryTest(zeit.cms.testing.FunctionalTestCase):

    layer = SearchLayer

    def test_query(self):
        q = zeit.find.search.query('Obama')
        result = zeit.find.search.search(q)
        self.assertEquals(606, result.hits)
        self.assertEquals(
            'http://xml.zeit.de/online/2007/01/Somalia',
            result.docs[0]['uniqueId'])
