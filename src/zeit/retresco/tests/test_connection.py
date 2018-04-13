# -*- coding: utf-8 -*-
from zeit.cms.checkout.helper import checked_out
from zeit.cms.interfaces import Result
from zeit.cms.workflow.interfaces import IPublishInfo
import gocept.testing.assertion
import json
import mock
import os
import pytest
import requests.adapters
import requests.exceptions
import time
import zeit.cms.tagging.interfaces
import zeit.connector.interfaces
import zeit.content.rawxml.rawxml
import zeit.content.text.text
import zeit.retresco.connection
import zeit.retresco.interfaces
import zeit.retresco.tagger
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
        with checked_out(self.repository['testcontent']):
            pass  # Trigger mock connector uuid creation
        self.layer['request_handler'].response_body = json.dumps({
            'body': '<body>lorem ipsum</body>'})
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        result = tms.get_article_body(self.repository['testcontent'])
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
            # Does not break on rows=0
            tms.get_topicpage_documents('tms-id', 0, 0)
            self.assertEqual(1, request.call_args[1]['params']['page'])

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
        with checked_out(self.repository['testcontent']):
            pass  # Trigger mock connector uuid creation

        def add_tag(label, typ, pinned):
            tag = zeit.retresco.tag.Tag(label, typ)
            tagger[tag.code] = tag
            if pinned:
                tagger.set_pinned(tagger.pinned + (tag.code,))
        tagger = zeit.retresco.tagger.Tagger(self.repository['testcontent'])
        add_tag('New York', 'location', True)
        add_tag('Obama', 'person', True)
        add_tag('Merkel', 'person', True)
        add_tag('Clinton', 'person', False)
        dav_tagger = zeit.connector.interfaces.IWebDAVProperties(tagger)

        self.layer['request_handler'].response_body = json.dumps({
            'entity_links': [
                # already linked: still shown
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
            'doc_type': 'article',
            'payload': {
                'tagging': {
                    name: value for (name, ns), value in dav_tagger.items()
                    if ns == 'http://namespaces.zeit.de/CMS/tagging'
                }
            },
        })
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        result = tms.get_article_keywords(self.repository['testcontent'])
        self.assertEqual(
            ['New York', 'Obama', 'Merkel', 'Clinton', 'Berlin'],
            [x.label for x in result])
        self.assertEqual('thema/newyork', result[0].link)


@pytest.mark.slow
class IntegrationTest(zeit.retresco.testing.FunctionalTestCase,
                      gocept.testing.assertion.String):

    level = 2

    # NOTE: enrich against tms.staging.zeit.de is notoriously flaky (sigh),
    # so if this fails, just run it again, chances are it will work then.

    def setUp(self):
        super(IntegrationTest, self).setUp()
        self.tms = zeit.retresco.connection.TMS(
            os.environ['ZEIT_RETRESCO_URL'])
        self.article = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/online/2007/01/Somalia')
        with checked_out(self.article):
            # Trigger mock connector uuid creation.
            # This also serves as test isolation, since we get a random uuid
            # on each run, with which we also clean up in TMS on tearDown.
            pass

    def tearDown(self):
        try:
            self.tms.delete_id(
                zeit.cms.content.interfaces.IUUID(self.article).id)
        except Exception as e:
            print(e)
        super(IntegrationTest, self).tearDown()

    def test_enrich_returns_keywords(self):
        keywords = self.tms.extract_keywords(self.article)
        self.assertIn(zeit.retresco.tag.Tag('Somalia', 'location'), keywords)

    def test_get_topicpages_has_expected_fields(self):
        pages = self.tms.get_topicpages()
        self.assertNotEqual(0, len(pages))
        page = pages[0]
        self.assertIn('id', page)
        self.assertIn('topic_type', page)
        self.assertIn('title', page)

    def test_can_retrieve_data_after_index(self):
        self.assertIn('doc_id', self.tms.index(self.article))
        data = self.tms.get_article_data(self.article)
        self.assertEqual(self.article.title, data['title'])

    def test_can_retrieve_body_after_publish(self):
        response = self.tms.enrich(self.article)
        self.assertIn('doc_id', self.tms.index(self.article, response['body']))
        self.tms.publish(self.article)
        body = self.tms.get_article_body(self.article)
        self.assertStartsWith('<body', body)


class TopiclistUpdateTest(zeit.retresco.testing.FunctionalTestCase):

    def test_updates_configured_content_and_publishes(self):
        self.repository['topics'] = zeit.content.rawxml.rawxml.RawXML()
        text = zeit.content.text.text.Text()
        text.text = ''
        self.repository['redirects'] = text

        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.retresco')
        config['topiclist'] = 'http://xml.zeit.de/topics'
        config['topic-redirect-id'] = 'http://xml.zeit.de/redirects'

        with mock.patch(
                'zeit.retresco.connection.TMS.get_all_topicpages',
                new=lambda x: iter([{
                    'id': 'berlin',
                    'title': 'Berlin',
                    'topic_type': 'location',
                    'redirect': '/thema/hamburg'}])):
            zeit.retresco.connection._update_topiclist()

        topics = self.repository['topics']
        self.assertEqual(True, IPublishInfo(topics).published)
        redirects = self.repository['redirects']
        self.assertEqual(True, IPublishInfo(redirects).published)
        self.assertIn('hamburg', redirects.text)

    def test_topiclist_produces_xml(self):
        pages = [{
            'id': 'berlin',
            'title': 'Berlin',
            'topic_type': 'location',
        }]
        xml = zeit.retresco.connection._build_topic_xml(pages)
        self.assertEqual('topics', xml.tag)
        topics = xml.xpath('//topic')
        self.assertEqual(1, len(topics))
        self.assertEqual('Berlin', topics[0].text)

    def test_topiclist_excludes_pages_with_redirect(self):
        pages = [{
            'id': 'berlin',
            'title': 'Berlin',
            'topic_type': 'location',
            'redirect': '/thema/hamburg'
        }]
        xml = zeit.retresco.connection._build_topic_xml(pages)
        self.assertEqual([], xml.xpath('//topic'))

    def test_redirects_include_pages_with_redirect(self):
        pages = [{
            'id': 'berlin',
            'title': 'Berlin',
            'topic_type': 'location',
            'redirect': '/thema/hamburg'
        }]
        text = zeit.retresco.connection._build_topic_redirects(pages)
        self.assertEllipsis(
            '...location = /thema/berlin { return 301 '
            'http://www.zeit.de/thema/hamburg; }...', text)


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
