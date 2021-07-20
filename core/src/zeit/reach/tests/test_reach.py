from zeit.reach.reach import Reach
import json
import zeit.cms.interfaces
import zeit.reach.testing


class ReachTest(zeit.reach.testing.FunctionalTestCase):

    def test_parses_response_and_resolves_content(self):
        self.layer['request_handler'].response_body = json.dumps([{
            'uniqueId': 'http://xml.zeit.de/testcontent',
            'score': 42,
        }])

        reach = Reach('http://localhost:%s' % self.layer['http_port'])
        (content,) = reach.get_ranking('views')

        self.assertEqual('http://xml.zeit.de/testcontent', content.uniqueId)
        self.assertTrue(
            zeit.reach.interfaces.IReachContent.providedBy(content))
        kpi = zeit.cms.content.interfaces.IKPI(content)
        self.assertTrue(zeit.reach.interfaces.IKPI.providedBy(kpi))
        self.assertEqual(42, kpi.score)

        (request,) = self.layer['request_handler'].requests
        self.assertEqual('/ranking/views?limit=3', request['path'])
