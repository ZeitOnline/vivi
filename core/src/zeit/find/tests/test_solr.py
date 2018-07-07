import zeit.cms.testing
import zeit.find.tests


class QueryTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.find.tests.LAYER

    def test_query(self):
        import zeit.find.solr
        self.layer.set_result(__name__, 'data/obama.json')
        q = zeit.find.solr.query('Obama')
        result = zeit.find.solr.search(q)
        self.assertEquals(606, result.hits)
        self.assertEquals(
            'http://xml.zeit.de/online/2007/01/Somalia',
            result.docs[0]['uniqueId'])
        req = self.layer.solr._send_request
        self.assertEqual(1, req.call_count)
        self.assertEqual('get', req.call_args[0][0])
        query = req.call_args[0][1]
        self.assertTrue(query.startswith(
            'select/?q=%28text%3A%28Obama%29+AND+NOT+ressort%3A%28News'))
        self.assertTrue('range' in query)
        self.assertTrue('range_details' in query)

    def test_suggest(self):
        import zeit.find.solr
        self.layer.set_result(__name__, 'data/obama.json')
        q = zeit.find.solr.suggest_query('Diet', 'title', ['author'])
        self.assertEqual(
            u'((title:(diet*) OR title:(diet)) AND (type:(author)))', q)
        zeit.find.solr.search(q, sort_order='title')
        req = self.layer.solr._send_request
        query = req.call_args[0][1]
        self.assertTrue(query.startswith(
            'select/?q=%28%28title%3A%28diet%2A%29+' +
            'OR+title%3A%28diet%29%29+AND+%28type%3A%28' +
            'author%29%29%29&sort=title+asc'),
            query)
