# -*- coding: utf-8 -*-
from zeit.retresco.tag import Tag
from zeit.cms.interfaces import Result
from zeit.cms.workflow.interfaces import IPublishInfo
import json
import lxml.builder
import mock
import pytest
import requests.adapters
import requests.exceptions
import requests.models
import requests.sessions
import time
import zeit.cms.tagging.interfaces
import zeit.content.rawxml.rawxml
import zeit.retresco.connection
import zeit.retresco.interfaces
import zeit.retresco.testing
import zope.component


class TMSTest(zeit.retresco.testing.FunctionalTestCase):

    def setUp(self):
        super(TMSTest, self).setUp()
        patcher = mock.patch(
            'zeit.retresco.convert.TMSRepresentation._validate')
        validate = patcher.start()
        validate.return_value = True
        self.addCleanup(patcher.stop)

    def test_extract_keywords_converts_response_to_tag_objects(self):
        self.layer['request_handler'].response_body = json.dumps({
            'rtr_persons': ['Merkel', 'Obama'],
            'rtr_locations': ['Berlin', 'Washington'],
        })
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        result = tms.extract_keywords(self.repository['testcontent'])
        self.assertEqual(['Berlin', 'Merkel', 'Obama', 'Washington'],
                         sorted([x.label for x in result]))

    def test_get_keywords_returns_a_list_of_tag_objects(self):
        self.layer['request_handler'].response_body = json.dumps({
            "entities": [{"entity_id": "e8ed9435b876196564bb86599009456cbb2aa",
                          "doc_count": 3,
                          "entity_name": "Schmerz",
                          "entity_type": "keyword"},
                         {"entity_id": "bf87d9ce8457a96fe2de1eac6d9614aa462ba",
                          "doc_count": 1,
                          "entity_name": u"Walter Schmögner",
                          "entity_type": "person"}],
            "num_found": 2})
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        result = list(tms.get_keywords('Sch'))
        self.assertEqual(2, len(result))
        self.assertTrue(zeit.cms.tagging.interfaces.ITag.providedBy(result[0]))
        self.assertEqual([u'Schmerz', u'Walter Schmögner'],
                         [x.label for x in result])

    def test_get_locations_returns_a_list_of_tag_objects(self):
        self.layer['request_handler'].response_body = json.dumps({
            "entities": [{
                "entity_id": "f1ec6233309adee0384d1b82962c2a074babe7a2",
                "doc_count": 1,
                "entity_name": "Kroatien",
                "entity_type": "location"}],
            "num_found": 1})
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        result = list(tms.get_locations('Kro'))
        self.assertTrue(zeit.cms.tagging.interfaces.ITag.providedBy(result[0]))
        self.assertEqual([u'Kroatien'], [x.label for x in result])

    def test_get_locations_filters_by_entity_type_location(self):
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        with mock.patch.object(tms, '_request') as request:
            request.return_value = {"entities": [], "num_found": 0}
            list(tms.get_locations(''))
            self.assertEqual({'q': '', 'item_type': 'location'},
                             request.call_args[1]['params'])

    def test_raises_technical_error_for_5xx(self):
        self.layer['request_handler'].response_code = 500
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        with self.assertRaises(zeit.retresco.interfaces.TechnicalError):
            tms.extract_keywords(self.repository['testcontent'])

    def test_raises_domain_error_for_4xx(self):
        self.layer['request_handler'].response_code = 400
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        with self.assertRaises(zeit.retresco.interfaces.TMSError):
            tms.extract_keywords(self.repository['testcontent'])

    def test_ignores_404_on_delete(self):
        self.layer['request_handler'].response_code = 404
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        tms.delete_id('any')

    def test_tms_returns_enriched_article_body(self):
        self.layer['request_handler'].response_body = json.dumps({
            'body': '<body>lorem ipsum</body>'})
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        result = tms.get_article_body('{urn:uuid:88a99fcc-0c52-4665}')
        self.assertEqual('<body>lorem ipsum</body>', result)

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
        self.layer['request_handler'].response_body = json.dumps({
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
            'keywords': [
                Tag('Berlin', 'keyword'), Tag('Washington', 'keyword')],
            'supertitle': 'supertitle',
            'title': 'title',
        }, result[0])

    def test_get_topicpages_pagination(self):
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        with mock.patch.object(tms, '_request') as request:
            request.return_value = {'num_found': 0, 'docs': []}
            # Default values
            tms.get_topicpages()
            self.assertEqual(1, request.call_args[1]['params']['page'])
            self.assertEqual(25, request.call_args[1]['params']['rows'])
            # Passes through rows
            tms.get_topicpages(0, 7)
            self.assertEqual(1, request.call_args[1]['params']['page'])
            self.assertEqual(7, request.call_args[1]['params']['rows'])
            # Calculates page from start
            tms.get_topicpages(5, 5)
            self.assertEqual(2, request.call_args[1]['params']['page'])
            tms.get_topicpages(10, 5)
            self.assertEqual(3, request.call_args[1]['params']['page'])

    def test_get_topicpages_dicts_have_id_and_title(self):
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        self.layer['request_handler'].response_body = json.dumps({
            'num_found': 1,
            'docs': [{
                'url': '/thema/mytopic',
                'doc_id': 'mytopic',
                'query_terms': ['Berlin', 'Washington'],
                'title': 'Mytopic',
                # lots of fields of the actual response omitted.
            }],
        })
        result = tms.get_topicpages()
        self.assertEqual(1, result.hits)
        self.assertEqual('mytopic', result[0]['id'])
        self.assertEqual('Mytopic', result[0]['title'])

    def test_topicpages_are_available_as_utility(self):
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        topics = zope.component.getUtility(
            zeit.cms.tagging.interfaces.ITopicpages)
        with mock.patch.object(tms, 'get_topicpages') as get:
            result = Result([{'id': 'mytopic', 'title': 'Mytopic'}])
            result.hits = 1
            get.return_value = result
            result = topics.get_topics()
            self.assertEqual(1, result.hits)
            self.assertEqual('mytopic', result[0]['id'])
            self.assertEqual('Mytopic', result[0]['title'])

    def test_get_all_topicpages_delegates_to_get_topicpages(self):
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        with mock.patch.object(tms, 'get_topicpages') as get:
            get.side_effect = [
                Result([{'id': 'mytopic', 'title': 'Mytopic'}]),
                Result(),
            ]
            result = list(tms.get_all_topicpages())
            self.assertEqual(1, len(result))
            self.assertEqual('mytopic', result[0]['id'])
            self.assertEqual('Mytopic', result[0]['title'])

    def test_get_article_keywords_order_is_given_by_cms_payload(self):
        self.layer['request_handler'].response_body = json.dumps({
            'entity_links': [
                # already linked: ignored
                {'key': 'Merkel', 'key_type': 'person', 'score': "10.0",
                 'status': 'linked', 'link': '/thema/merkel'},
                # pinned: comes first
                {'key': 'Obama', 'key_type': 'person', 'score': "8.0",
                 'status': 'not_linked', 'link': '/thema/obama'},
                # not pinned: after pinned ones, by score
                {'key': 'Clinton', 'key_type': 'person', 'score': "6.0",
                 'status': 'not_linked', 'link': '/thema/clinton'},
                # not in CMS list: after pinned ones, by score
                {'key': 'Berlin', 'key_type': 'location', 'score': "5.0",
                 'status': 'not_linked', 'link': '/thema/berlin'},
                # no link: ignored
                {'key': 'Washington', 'key_type': 'location', 'score': "3.0",
                 'status': 'not_linked', 'link': None},
                # pinned: comes first
                {'key': 'New York', 'key_type': 'location', 'score': "1.0",
                 'status': 'not_linked', 'link': '/thema/newyork'},
            ],
            'payload': {
                'keywords': [
                    {'label': 'New York', 'entity_type': 'location',
                     'pinned': True},
                    {'label': 'Obama', 'entity_type': 'person',
                     'pinned': True},
                    {'label': 'Merkel', 'entity_type': 'person',
                     'pinned': True},
                    {'label': 'Clinton', 'entity_type': 'person',
                     'pinned': False},
                ],
            },
        })
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        result = tms.get_article_keywords('myid')
        self.assertEqual(
            ['New York', 'Obama', 'Clinton', 'Berlin'],
            [x.label for x in result])
        self.assertEqual('thema/newyork', result[0].link)


class TopiclistUpdateTest(zeit.retresco.testing.FunctionalTestCase):

    def test_updates_configured_content_and_publishes(self):
        self.repository['topics'] = zeit.content.rawxml.rawxml.RawXML()
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.retresco')
        config['topiclist'] = 'http://xml.zeit.de/topics'
        with mock.patch('zeit.retresco.connection._build_topic_xml') as xml:
            E = lxml.builder.ElementMaker()
            xml.return_value = E.topics(
                E.topic('Berlin', url_value='berlin')
            )
            zeit.retresco.connection._update_topiclist()
        topics = self.repository['topics']
        self.assertEqual(1, len(topics.xml.xpath('//topic')))
        self.assertEqual('topics', topics.xml.tag)
        self.assertEqual('Berlin', topics.xml.find('topic')[0])
        self.assertEqual(True, IPublishInfo(topics).published)


class SlowAdapter(requests.adapters.BaseAdapter):

    def send(self, request, **kwargs):
        time.sleep(request.headers.get('X-Sleep', 0))
        return requests.Response()

    def close(self):
        pass


class SignalTimeoutTest(zeit.retresco.testing.FunctionalTestCase):

    def setUp(self):
        super(SignalTimeoutTest, self).setUp()
        self.session = requests.Session()
        self.session.mount('slow://', SlowAdapter())

    @pytest.mark.slow
    def test_signal_timeout_is_not_invoked_on_timeout_tuple(self):
        # If someone specifically set a connect and read timeout tuple,
        # we want to preserve requests' intended behaviour.
        # SlowAdapter ignores touple timeouts, so lets see if our signal
        # timeout patch leaves the slow request be slow.
        resp = self.session.get(
            'slow://xml.zeit.de/index',
            headers={'X-Sleep': 0.2}, timeout=(0.01, 0.01))
        self.assertTrue(isinstance(resp, requests.Response))

    @pytest.mark.slow
    def test_signal_timeout_is_not_invoked_in_worker_thread(self):
        # Registering signal handlers can only be done within a main thread.
        # If it fails, we revert to requests original timeout mechanics.
        # This test also utilizes SlowAdapter ignoring the timeout kwarg.
        with mock.patch('signal.signal') as sig_func:
            sig_func.side_effect = ValueError()
            resp = self.session.get(
                'slow://xml.zeit.de/index',
                headers={'X-Sleep': 0.1}, timeout=0.01)
            self.assertTrue(isinstance(resp, requests.Response))

    @pytest.mark.slow
    def test_signal_timeout_should_abort_slow_responses(self):
        # Finally, we want to see a timeout exception risen by our patched
        # signal request function.
        with self.assertRaises(requests.exceptions.Timeout):
            self.session.get(
                'slow://xml.zeit.de/index',
                headers={'X-Sleep': 0.1}, timeout=0.01)
