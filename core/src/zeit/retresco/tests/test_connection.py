# -*- coding: utf-8 -*-
from unittest import mock
from zeit.cms.checkout.helper import checked_out
from zeit.cms.interfaces import Result
from zeit.cms.workflow.interfaces import IPublishInfo
import json
import os
import pytest
import urllib.parse
import zeit.cms.tagging.interfaces
import zeit.cms.tagging.tag
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
        super().setUp()
        patcher = mock.patch(
            'zeit.retresco.convert.TMSRepresentation._validate')
        validate = patcher.start()
        validate.return_value = True
        self.addCleanup(patcher.stop)

    def add_tag(self, tagger, label, typ, pinned):
        tag = zeit.cms.tagging.tag.Tag(label, typ)
        tagger[tag.code] = tag
        if pinned:
            tagger.set_pinned(tagger.pinned + (tag.code,))

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
                          "entity_name": "Walter Schmögner",
                          "entity_type": "person"}],
            "num_found": 2})
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        result = list(tms.get_keywords('Sch'))
        self.assertEqual(2, len(result))
        self.assertTrue(zeit.cms.tagging.interfaces.ITag.providedBy(result[0]))
        self.assertEqual(['Schmerz', 'Walter Schmögner'],
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
        self.assertEqual(['Kroatien'], [x.label for x in result])

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

    def test_get_article_topiclinks_order_is_given_by_cms_payload(self):
        with checked_out(self.repository['testcontent']):
            pass  # Trigger mock connector uuid creation

        tagger = zeit.retresco.tagger.Tagger(self.repository['testcontent'])
        self.add_tag(tagger, 'New York', 'location', True)
        self.add_tag(tagger, 'Obama', 'person', True)
        self.add_tag(tagger, 'Merkel', 'person', True)
        self.add_tag(tagger, 'Clinton', 'person', False)
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
        result = tms.get_article_topiclinks(self.repository['testcontent'])
        self.assertEqual(
            ['New York', 'Obama', 'Merkel', 'Clinton', 'Berlin'],
            [x.label for x in result])
        self.assertEqual('thema/newyork', result[0].link)

    def test_get_article_topiclinks_uses_published_content_endpoint_as_default(
            self):
        with checked_out(self.repository['testcontent']):
            pass  # Trigger mock connector uuid creation
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        tms.get_article_topiclinks(self.repository['testcontent'])
        # First requests will be enrich and index
        content = self.repository['testcontent']
        uuid = zeit.cms.content.interfaces.IUUID(content).id
        self.assertEqual(['{} {}'.format(r['verb'], urllib.parse.unquote(
            r['path'])) for r in self.layer['request_handler'].requests], [
            'GET /content/{}'.format(uuid),
            'POST /enrich?in-text-linked',
            'POST /another-tms/enrich?in-text-linked',
            'PUT /content/{}'.format(uuid),
            'PUT /another-tms/content/{}'.format(uuid),
            'GET /in-text-linked-documents/{}'.format(uuid),
        ])

    def test_get_article_topiclinks_uses_preview_endpoint_if_param_set(self):
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        tms.get_article_topiclinks(self.repository['testcontent'],
                                   published=False)
        self.assertEqual('/in-text-linked-documents-preview',
                         self.layer['request_handler'].requests[0].get('path'))

    def test_get_content_containing_topicpages_returns_list_of_tags(self):
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        self.layer['request_handler'].response_body = json.dumps({
            'num_found': 1,
            'docs': [{
                "doc_id": "arbeit",
                "name": "Arbeit",
                "title": "arbeit",
                "topic_type": "keyword",
                "url": "/thema/arbeit"
                # lots of fields of the actual response omitted.
            }],
        })
        article = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/online/2007/01/Somalia')
        result = tms.get_content_containing_topicpages(article)
        self.assertEqual('Arbeit', result[0].label)
        self.assertEqual('keyword', result[0].entity_type)


@pytest.mark.slow()
class IntegrationTest(zeit.retresco.testing.FunctionalTestCase):

    level = 2

    # NOTE: enrich against tms.staging.zeit.de is notoriously flaky (sigh),
    # so if this fails, just run it again, chances are it will work then.

    def setUp(self):
        super().setUp()
        self.tms = zeit.retresco.connection.TMS(
            primary={'url': os.environ['ZEIT_RETRESCO_URL']})
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
        super().tearDown()

    def test_enrich_returns_keywords(self):
        keywords = self.tms.extract_keywords(self.article)
        self.assertIn(
            zeit.cms.tagging.tag.Tag('Somalia', 'location'), keywords)

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
        data = self.tms.index(self.article, {'body': response['body']})
        self.assertIn('doc_id', data)
        self.tms.publish(self.article)
        body = self.tms.get_article_body(self.article)
        self.assertStartsWith('<body', body)

    def test_get_content_related_topicpages_works_without_keywords(self):
        assert self.article.keywords == ()
        assert self.tms.get_content_related_topicpages(self.article) == []


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
                return_value=[{
                    'id': 'berlin',
                    'title': 'Berlin',
                    'topic_type': 'location',
                    'redirect': '/thema/hamburg'}]):
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
            'kpi_1': 42,
        }]
        xml = zeit.retresco.connection._build_topic_xml(pages)
        self.assertEqual('topics', xml.tag)
        topics = xml.xpath('//topic')
        self.assertEqual(1, len(topics))
        self.assertEqual('Berlin', topics[0].text)
        self.assertEqual('42', topics[0].get('kpi_1'))
        self.assertEqual('location', topics[0].get('type'))

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
            '.../thema/berlin = http://www.zeit.de/thema/hamburg\n', text)
