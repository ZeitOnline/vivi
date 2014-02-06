# Copyright (c) 2008-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.httpserverlayer.wsgi
import gocept.selenium
import mock
import pkg_resources
import zeit.cms.testing
import zope.component

product_config = """\
<product-config zeit.solr>
    solr-url http://internal.invalid
    public-solr-url http://public.invalid
    second-solr-url http://public.invalid
</product-config>
"""


SearchZCMLLayer = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=zeit.cms.testing.cms_product_config + product_config)


class SearchLayer(SearchZCMLLayer):

    @classmethod
    def setUp(cls):
        import zeit.solr.interfaces
        cls.solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def testSetUp(cls):
        cls.solr._send_request = mock.Mock()

    @classmethod
    def testTearDown(cls):
        del cls.solr._send_request

    @classmethod
    def set_result(cls, package, filename):
        cls.solr._send_request.return_value = pkg_resources.resource_string(
            package, filename)


WSGI_LAYER = zeit.cms.testing.WSGILayer(name='WSGILayer', bases=(SearchLayer,))
HTTP_LAYER = gocept.httpserverlayer.wsgi.Layer(
    name='HTTPLayer', bases=(WSGI_LAYER,))
SeleniumLayer = gocept.selenium.RCLayer(
    name='SeleniumLayer', bases=(HTTP_LAYER,))


class QueryTest(zeit.cms.testing.FunctionalTestCase):

    layer = SearchLayer

    def test_query(self):
        import zeit.find.search
        self.layer.set_result(__name__, 'testdata/obama.json')
        q = zeit.find.search.query('Obama')
        result = zeit.find.search.search(q)
        self.assertEquals(606, result.hits)
        self.assertEquals(
            'http://xml.zeit.de/online/2007/01/Somalia',
            result.docs[0]['uniqueId'])
        req = self.layer.solr._send_request
        self.assertEqual(1, req.call_count)
        self.assertEqual('GET', req.call_args[0][0])
        query = req.call_args[0][1]
        self.assertTrue(query.startswith(
            '/select/?q=%28text%3A%28Obama%29+AND+NOT+ressort%3A%28News'))
        self.assertTrue('range' in query)
        self.assertTrue('range_details' in query)

    def test_suggest(self):
        import zeit.find.search
        self.layer.set_result(__name__, 'testdata/obama.json')
        q = zeit.find.search.suggest_query('Diet','title',['author'])
        self.assertEqual(
            u'((title:(diet*) OR title:(diet)) AND (type:(author)))',
            q)        
        zeit.find.search.search(q, sort_order='title')
        req = self.layer.solr._send_request
        query = req.call_args[0][1]
        self.assertTrue(query.startswith(
            '/select/?q=%28%28title%3A%28diet%2A%29+'+
            'OR+title%3A%28diet%29%29+AND+%28type%3A%28'+
            'author%29%29%29&sort=title+asc'),
            query)
