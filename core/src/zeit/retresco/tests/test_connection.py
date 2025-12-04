# -*- coding: utf-8 -*-
from unittest import mock
import json
import urllib.parse

from sqlalchemy import select
import transaction
import zope.component

from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.interfaces import Result
from zeit.cms.workflow.interfaces import IPublish, IPublishInfo
from zeit.connector.models import Content
import zeit.cms.tagging.interfaces
import zeit.cms.tagging.tag
import zeit.connector.interfaces
import zeit.content.rawxml.rawxml
import zeit.content.text.text
import zeit.kpi.interfaces
import zeit.kpi.update
import zeit.retresco.connection
import zeit.retresco.interfaces
import zeit.retresco.tagger
import zeit.retresco.testing


HTTP_LAYER = zeit.cms.testing.HTTPLayer()
CONNECTION_LAYER = zeit.cms.testing.Layer(
    (zeit.retresco.testing.ZOPE_LAYER, HTTP_LAYER), name='ConnectionLayer'
)


class HTTPTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = CONNECTION_LAYER

    def testSetUp(self):
        # Remove TMS requests triggered by e.g. ZopeLayer.testSetUp()
        self.layer['request_handler'].reset()


class TMSTest(HTTPTestCase):
    def setUp(self):
        super().setUp()
        patcher = mock.patch('zeit.retresco.convert.TMSRepresentation._is_valid')
        validate = patcher.start()
        validate.return_value = True
        self.addCleanup(patcher.stop)

        self.tms = zeit.retresco.connection.TMS(f'http://localhost:{self.layer["http_port"]}')

    def add_tag(self, tagger, label, typ, pinned):
        tag = zeit.cms.tagging.tag.Tag(label, typ)
        tagger[tag.code] = tag
        if pinned:
            tagger.set_pinned(tagger.pinned + (tag.code,))

    def test_extract_keywords_converts_response_to_tag_objects(self):
        self.layer['request_handler'].response_body = json.dumps(
            {
                'rtr_persons': ['Merkel', 'Obama'],
                'rtr_locations': ['Berlin', 'Washington'],
            }
        )
        result = self.tms.extract_keywords(self.repository['testcontent'])
        self.assertEqual(
            ['Berlin', 'Merkel', 'Obama', 'Washington'], sorted([x.label for x in result])
        )

    def test_get_keywords_returns_a_list_of_tag_objects(self):
        self.layer['request_handler'].response_body = json.dumps(
            {
                'entities': [
                    {
                        'entity_id': 'e8ed9435b876196564bb86599009456cbb2aa',
                        'doc_count': 3,
                        'entity_name': 'Schmerz',
                        'entity_type': 'keyword',
                    },
                    {
                        'entity_id': 'bf87d9ce8457a96fe2de1eac6d9614aa462ba',
                        'doc_count': 1,
                        'entity_name': 'Walter Schmögner',
                        'entity_type': 'person',
                    },
                ],
                'num_found': 2,
            }
        )
        result = list(self.tms.get_keywords('Sch'))
        self.assertEqual(2, len(result))
        self.assertTrue(zeit.cms.tagging.interfaces.ITag.providedBy(result[0]))
        self.assertEqual(['Schmerz', 'Walter Schmögner'], [x.label for x in result])

    def test_get_locations_returns_a_list_of_tag_objects(self):
        self.layer['request_handler'].response_body = json.dumps(
            {
                'entities': [
                    {
                        'entity_id': 'f1ec6233309adee0384d1b82962c2a074babe7a2',
                        'doc_count': 1,
                        'entity_name': 'Kroatien',
                        'entity_type': 'location',
                    }
                ],
                'num_found': 1,
            }
        )
        result = list(self.tms.get_locations('Kro'))
        self.assertTrue(zeit.cms.tagging.interfaces.ITag.providedBy(result[0]))
        self.assertEqual(['Kroatien'], [x.label for x in result])

    def test_get_locations_filters_by_entity_type_location(self):
        with mock.patch.object(self.tms, '_request') as request:
            request.return_value = {'entities': [], 'num_found': 0}
            list(self.tms.get_locations(''))
            self.assertEqual({'q': '', 'item_type': 'location'}, request.call_args[1]['params'])

    def test_raises_technical_error_for_5xx(self):
        self.layer['request_handler'].response_code = 500
        with self.assertRaises(zeit.retresco.interfaces.TechnicalError):
            self.tms.extract_keywords(self.repository['testcontent'])

    def test_raises_domain_error_for_4xx(self):
        self.layer['request_handler'].response_code = 400
        with self.assertRaises(zeit.retresco.interfaces.TMSError):
            self.tms.extract_keywords(self.repository['testcontent'])

    def test_ignores_404_on_delete(self):
        self.layer['request_handler'].response_code = 404
        self.tms.delete_id('any')

    def test_tms_returns_enriched_article_body(self):
        with checked_out(self.repository['testcontent']):
            pass  # Trigger mock connector uuid creation
        self.layer['request_handler'].response_body = json.dumps(
            {'body': '<body>lorem ipsum</body>'}
        )
        result = self.tms.get_article_body(self.repository['testcontent'])
        self.assertEqual('<body>lorem ipsum</body>', result)

    def test_get_topicpages_pagination(self):
        with mock.patch.object(self.tms, '_request') as request:
            request.return_value = {'num_found': 0, 'docs': []}
            # Default values
            self.tms.get_topicpages()
            self.assertEqual(1, request.call_args[1]['params']['page'])
            self.assertEqual(25, request.call_args[1]['params']['rows'])
            # Passes through rows
            self.tms.get_topicpages(0, 7)
            self.assertEqual(1, request.call_args[1]['params']['page'])
            self.assertEqual(7, request.call_args[1]['params']['rows'])
            # Calculates page from start
            self.tms.get_topicpages(5, 5)
            self.assertEqual(2, request.call_args[1]['params']['page'])
            self.tms.get_topicpages(10, 5)
            self.assertEqual(3, request.call_args[1]['params']['page'])

    def test_get_topicpages_dicts_have_id_and_title(self):
        self.layer['request_handler'].response_body = json.dumps(
            {
                'num_found': 1,
                'docs': [
                    {
                        'url': '/thema/mytopic',
                        'doc_id': 'mytopic',
                        'query_terms': ['Berlin', 'Washington'],
                        'title': 'Mytopic',
                        # lots of fields of the actual response omitted.
                    }
                ],
            }
        )
        result = self.tms.get_topicpages()
        self.assertEqual(1, result.hits)
        self.assertEqual('mytopic', result[0]['id'])
        self.assertEqual('Mytopic', result[0]['title'])

    def test_get_all_topicpages_delegates_to_get_topicpages(self):
        with mock.patch.object(self.tms, 'get_topicpages') as get:
            get.side_effect = [
                Result([{'id': 'mytopic', 'title': 'Mytopic'}]),
                Result(),
            ]
            result = list(self.tms.get_all_topicpages())
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

        self.layer['request_handler'].response_body = json.dumps(
            {
                'entity_links': [
                    # already linked: still shown
                    {
                        'key': 'Merkel',
                        'key_type': 'person',
                        'score': '10.0',
                        'status': 'linked',
                        'link': '/thema/merkel',
                    },
                    # pinned: comes first
                    {
                        'key': 'Obama',
                        'key_type': 'person',
                        'score': '8.0',
                        'status': 'not_linked',
                        'link': '/thema/obama',
                    },
                    # not pinned: after pinned ones, by score
                    {
                        'key': 'Clinton',
                        'key_type': 'person',
                        'score': '6.0',
                        'status': 'not_linked',
                        'link': '/thema/clinton',
                    },
                    # not in CMS list: after pinned ones, by score
                    {
                        'key': 'Berlin',
                        'key_type': 'location',
                        'score': '5.0',
                        'status': 'not_linked',
                        'link': '/thema/berlin',
                    },
                    # no link: ignored
                    {
                        'key': 'Washington',
                        'key_type': 'location',
                        'score': '3.0',
                        'status': 'not_linked',
                        'link': None,
                    },
                    # pinned: comes first
                    {
                        'key': 'New York',
                        'key_type': 'location',
                        'score': '1.0',
                        'status': 'not_linked',
                        'link': '/thema/newyork',
                    },
                ],
                'doc_type': 'article',
                'payload': {
                    'tagging': {
                        name: value
                        for (name, ns), value in dav_tagger.items()
                        if ns == 'http://namespaces.zeit.de/CMS/tagging'
                    }
                },
            }
        )
        result = self.tms.get_article_topiclinks(self.repository['testcontent'])
        self.assertEqual(
            ['New York', 'Obama', 'Merkel', 'Clinton', 'Berlin'], [x.label for x in result]
        )
        self.assertEqual('thema/newyork', result[0].link)

    def test_get_article_topiclinks_uses_published_content_endpoint_as_default(self):
        self.tms.get_article_topiclinks(self.repository['testcontent'])
        content = self.repository['testcontent']
        uuid = zeit.cms.content.interfaces.IUUID(content).id
        self.assertEqual(
            [
                '{} {}'.format(r['verb'], urllib.parse.unquote(r['path']))
                for r in self.layer['request_handler'].requests
            ],
            ['GET /in-text-linked-documents/{}'.format(uuid)],
        )

    def test_get_article_topiclinks_uses_preview_endpoint_if_param_set(self):
        self.tms.get_article_topiclinks(self.repository['testcontent'], published=False)
        self.assertEqual(
            '/in-text-linked-documents-preview',
            self.layer['request_handler'].requests[0].get('path'),
        )

    def test_get_content_containing_topicpages_returns_list_of_tags(self):
        self.layer['request_handler'].response_body = json.dumps(
            {
                'num_found': 1,
                'docs': [
                    {
                        'doc_id': 'arbeit',
                        'name': 'Arbeit',
                        'title': 'arbeit',
                        'topic_type': 'keyword',
                        'url': '/thema/arbeit',
                        # lots of fields of the actual response omitted.
                    }
                ],
            }
        )
        article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/article')
        result = self.tms.get_content_containing_topicpages(article)
        self.assertEqual('Arbeit', result[0].label)
        self.assertEqual('keyword', result[0].entity_type)

    def test_disable_tms(self):
        FEATURE_TOGGLES.set('disable_tms')
        self.layer['request_handler'].response_body = json.dumps(
            {
                'rtr_persons': ['Merkel', 'Obama'],
            }
        )
        result = self.tms.extract_keywords(self.repository['testcontent'])
        self.assertEqual([], result)


class TopiclistUpdateTest(zeit.retresco.testing.FunctionalTestCase):
    def test_updates_configured_content_and_publishes(self):
        self.repository['topics'] = zeit.content.rawxml.rawxml.RawXML()
        text = zeit.content.text.text.Text()
        text.text = ''
        self.repository['redirects'] = text

        zeit.cms.config.set('zeit.retresco', 'topiclist', 'http://xml.zeit.de/topics')
        zeit.cms.config.set('zeit.retresco', 'topic-redirect-id', 'http://xml.zeit.de/redirects')

        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        tms.get_all_topicpages.return_value = [
            {
                'id': 'berlin',
                'title': 'Berlin',
                'topic_type': 'location',
                'redirect': '/thema/hamburg',
            }
        ]
        zeit.retresco.connection._update_topiclist()

        topics = self.repository['topics']
        self.assertEqual(True, IPublishInfo(topics).published)
        redirects = self.repository['redirects']
        self.assertEqual(True, IPublishInfo(redirects).published)
        self.assertIn('hamburg', redirects.text)

    def test_topiclist_produces_xml(self):
        pages = [
            {
                'id': 'berlin',
                'title': 'Berlin',
                'topic_type': 'location',
                'kpi_1': 42,
            }
        ]
        xml = zeit.retresco.connection._build_topic_xml(pages)
        self.assertEqual('topics', xml.tag)
        topics = xml.xpath('//topic')
        self.assertEqual(1, len(topics))
        self.assertEqual('Berlin', topics[0].text)
        self.assertEqual('42', topics[0].get('kpi_1'))
        self.assertEqual('location', topics[0].get('type'))

    def test_topiclist_excludes_pages_with_redirect(self):
        pages = [
            {
                'id': 'berlin',
                'title': 'Berlin',
                'topic_type': 'location',
                'redirect': '/thema/hamburg',
            }
        ]
        xml = zeit.retresco.connection._build_topic_xml(pages)
        self.assertEqual([], xml.xpath('//topic'))

    def test_redirects_include_pages_with_redirect(self):
        pages = [
            {
                'id': 'berlin',
                'title': 'Berlin',
                'topic_type': 'location',
                'redirect': '/thema/hamburg',
            }
        ]
        text = zeit.retresco.connection._build_topic_redirects(pages)
        self.assertEllipsis('.../thema/berlin = http://www.zeit.de/thema/hamburg\n', text)


class KPIUpdateTest(zeit.retresco.testing.FunctionalTestCase):
    def test_event_calls_update_kpi(self):
        IPublish(self.repository['testcontent']).publish(background=False)

        kpi = zope.component.getUtility(zeit.kpi.interfaces.IKPIDatasource)
        data = mock.Mock(visits=1, comments=2, subscriptions=3)
        kpi.result = [(self.repository['testcontent'], data)]
        zeit.kpi.update.update(select(Content), 1, 1)

        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        self.assertEqual((self.repository['testcontent'], data), tms.update_kpi.call_args[0])
        self.assertTrue(tms.publish.called)

    def test_update_kpi_does_not_publish_changed_objects(self):
        IPublish(self.repository['testcontent']).publish(background=False)
        with checked_out(self.repository['testcontent']):
            pass  # update date_last_modified
        transaction.commit()

        kpi = zope.component.getUtility(zeit.kpi.interfaces.IKPIDatasource)
        kpi.result = [
            (self.repository['testcontent'], mock.Mock(visits=1, comments=2, subscriptions=3))
        ]
        zeit.kpi.update.update(select(Content), 1, 10)

        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        self.assertTrue(tms.update_kpi.called)
        self.assertFalse(tms.publish.called)
