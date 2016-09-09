# -*- coding: utf-8 -*-
from zeit.retresco.testing import RequestHandler as TEST_SERVER
import json
import mock
import zeit.cms.tagging.interfaces
import zeit.cms.testing
import zeit.retresco.interfaces
import zeit.retresco.testing
import zope.component


class TMSTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.retresco.testing.ZCML_LAYER

    def setUp(self):
        super(TMSTest, self).setUp()
        patcher = mock.patch(
            'zeit.retresco.convert.TMSRepresentation._validate')
        validate = patcher.start()
        validate.return_value = True
        self.addCleanup(patcher.stop)

    def test_extract_keywords_converts_response_to_tag_objects(self):
        TEST_SERVER.response_body = json.dumps({
            'rtr_persons': ['Merkel', 'Obama'],
            'rtr_locations': ['Berlin', 'Washington'],
        })
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        result = tms.extract_keywords(self.repository['testcontent'])
        self.assertEqual(['Berlin', 'Merkel', 'Obama', 'Washington'],
                         sorted([x.label for x in result]))

    def test_search_keywords_returns_a_list_of_tag_objects(self):
        TEST_SERVER.response_body = json.dumps({
            "entities": [{"entity_id": "e8ed9435b876196564bb86599009456cbb2aa",
                          "doc_count": 3,
                          "entity_name": "Schmerz",
                          "entity_type": "keyword"},
                         {"entity_id": "bf87d9ce8457a96fe2de1eac6d9614aa462ba",
                          "doc_count": 1,
                          "entity_name": "Walter Schmögner",
                          "entity_type": "person"}],
            "num_found": 2})
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        result = list(tms.get_keywords('Sch'))
        self.assertEqual(2, len(result))
        self.assertTrue(zeit.cms.tagging.interfaces.ITag.providedBy(result[0]))
        self.assertEqual([u'Schmerz', u'Walter Schmögner'],
                         [x.label for x in result])

    def test_raises_technical_error_for_5xx(self):
        TEST_SERVER.response_code = 500
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        with self.assertRaises(zeit.retresco.interfaces.TechnicalError):
            tms.extract_keywords(self.repository['testcontent'])

    def test_raises_domain_error_for_4xx(self):
        TEST_SERVER.response_code = 400
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        with self.assertRaises(zeit.retresco.interfaces.TMSError):
            tms.extract_keywords(self.repository['testcontent'])

    def test_ignores_404_on_delete(self):
        TEST_SERVER.response_code = 404
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        tms.delete_id('any')

    def test_get_topicpage_documents_pagination(self):
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        with mock.patch.object(tms, '_request') as request:
            request.return_value = {'num_found': 0, 'docs': []}
            # Default values
            tms.get_topicpage_documents('tms-id')
            self.assertEqual(1, request.call_args[1]['params']['page'])
            self.assertEqual(25, request.call_args[1]['params']['rows'])
            # Passes through rows
            tms.get_topicpage_documents('tms-id', 0, 7)
            self.assertEqual(1, request.call_args[1]['params']['page'])
            self.assertEqual(7, request.call_args[1]['params']['rows'])
            # Calculates page from start
            tms.get_topicpage_documents('tms-id', 5, 5)
            self.assertEqual(2, request.call_args[1]['params']['page'])
            tms.get_topicpage_documents('tms-id', 10, 5)
            self.assertEqual(3, request.call_args[1]['params']['page'])

    def test_get_topicpage_pulls_up_payload_keys(self):
        TEST_SERVER.response_body = json.dumps({
            'num_found': 1,
            'docs': [{
                'url': '/testcontent',
                'doc_type': 'testcontenttype',
                'doc_id': 'uuid',
                'rtr_keywords': ['Berlin', 'Washington'],
                'payload': {
                    'supertitle': 'supertitle',
                    'title': 'title',
                }
            }],
        })
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        result = tms.get_topicpage_documents('tms-id')
        self.assertEqual({
            'uniqueId': 'http://xml.zeit.de/testcontent',
            'doc_type': 'testcontenttype',
            'doc_id': 'uuid',
            'rtr_keywords': ['Berlin', 'Washington'],
            'supertitle': 'supertitle',
            'title': 'title',
        }, result[0])
