# Copyright (c) 2008-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import os
import pkg_resources
import unittest
import zeit.cms.testing
import zeit.find.search
import zope.app.testing.functional

product_config = """\
<product-config zeit.solr>
    solr-url file://%s
    public-solr-url file://%s
</product-config>
""" % (pkg_resources.resource_filename(__name__, 'testdata'),
       pkg_resources.resource_filename(__name__, 'testdata'))


SearchLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'SearchLayer', allow_teardown=True,
    product_config=product_config)


class QueryTest(zeit.cms.testing.FunctionalTestCase):

    layer = SearchLayer

    def test_query(self):
        q = zeit.find.search.query('Obama')
        result = zeit.find.search.search(q)
        self.assertEquals(606, result.hits)
        self.assertEquals(
            'http://xml.zeit.de/online/2007/01/Somalia',
            result.docs[0]['uniqueId'])
