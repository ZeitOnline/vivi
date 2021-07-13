from zeit.reach.reach import Reach
import json
import zeit.cms.interfaces
import zeit.reach.testing


class ReachTest(zeit.reach.testing.FunctionalTestCase):

    def test_parses_response_and_retrieves_metada_from_es(self):
        self.layer['request_handler'].response_body = json.dumps([{
            'location': '/my-article',
            'score': 42,
        }])
        self.layer['elasticsearch'].search.return_value = (
            zeit.cms.interfaces.Result([{
                'doc_type': 'testcontenttype', 'url': '/my-article'}]))

        reach = Reach('http://localhost:%s' % self.layer['http_port'])
        (content,) = reach.get_ranking('views')

        self.assertEqual('http://xml.zeit.de/my-article', content.uniqueId)
        self.assertTrue(
            zeit.reach.interfaces.IReachContent.providedBy(content))
        kpi = zeit.cms.content.interfaces.IKPI(content)
        self.assertTrue(zeit.reach.interfaces.IKPI.providedBy(kpi))
        self.assertEqual(42, kpi.score)

        (request,) = self.layer['request_handler'].requests
        self.assertEqual('/ranking/views?limit=3', request['path'])
