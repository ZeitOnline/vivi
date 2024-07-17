import unittest

import lxml.etree
import pendulum
import pytest
import requests_mock
import zope.app.appsetup.product
import zope.component
import zope.i18n

from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.interfaces import ICMSContent
from zeit.cms.workflow.interfaces import IPublish, IPublisher, IPublishInfo
from zeit.content.image.testing import create_image_group_with_master_image
import zeit.cms.related.interfaces
import zeit.cms.tagging.tag
import zeit.cms.tagging.testing
import zeit.cms.testing
import zeit.content.author.author
import zeit.objectlog.interfaces
import zeit.workflow.interfaces
import zeit.workflow.publish
import zeit.workflow.publish_3rdparty
import zeit.workflow.publisher
import zeit.workflow.testing


class Publisher3rdPartyTest(zeit.workflow.testing.FunctionalTestCase):
    layer = zeit.workflow.testing.ARTICLE_LAYER

    def setUp(self):
        super().setUp()
        self.gsm = zope.component.getGlobalSiteManager()
        self.gsm.registerUtility(zeit.workflow.publisher.Publisher(), IPublisher)

    @pytest.fixture(autouse=True)
    def _caplog(self, caplog):
        self.caplog = caplog

    def test_ignore_3rdparty_list_is_respected(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        self.assertFalse(IPublishInfo(article).published)
        article_2 = ICMSContent('http://xml.zeit.de/online/2007/01/Schrempp')
        IPublishInfo(article_2).published = True
        self.assertTrue(IPublishInfo(article_2).published)
        with requests_mock.Mocker() as rmock:
            zeit.workflow.publish_3rdparty.PublisherData.ignore = ['speechbert']
            response = rmock.post('http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=True)
            (result,) = response.last_request.json()
            assert 'speechbert' not in result
            assert 'authordashboard' in result

            zeit.workflow.publish_3rdparty.PublisherData.ignore = ['speechbert']
            FEATURE_TOGGLES.set('disable_publisher_authordashboard')
            response = rmock.post('http://localhost:8060/test/publish', status_code=200)
            IPublish(article_2).publish(background=False)
            (result,) = response.last_request.json()
            assert 'speechbert' not in result
            assert 'authordashboard' not in result
        zeit.workflow.publish_3rdparty.PublisherData.ignore = []  # reset
        self.assertTrue(IPublishInfo(article).published)
        self.assertTrue(IPublishInfo(article_2).published)

    def test_authordashboard_is_notified(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        self.assertFalse(IPublishInfo(article).published)
        with requests_mock.Mocker() as rmock:
            response = rmock.post('http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            result_authordashboard = result['authordashboard']
            self.assertEqual({}, result_authordashboard)
        self.assertTrue(IPublishInfo(article).published)

    def test_bigquery_is_published(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        self.assertFalse(IPublishInfo(article).published)
        with requests_mock.Mocker() as rmock:
            response = rmock.post('http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            result_bq = result['bigquery']
            self.assertEqual(
                'http://localhost/live-prefix/online/2007/01/Somalia',
                result_bq['properties']['meta']['url'],
            )
        self.assertTrue(IPublishInfo(article).published)

    def test_video_contains_seo_slug_in_url(self):
        from zeit.content.video.video import Video

        video = Video()
        video.supertitle = 'seo slug'
        video.title = 'cookies'
        video.uniqueId = 'http://xml.zeit.de/video'
        json = zope.component.getAdapter(
            video, zeit.workflow.interfaces.IPublisherData, name='bigquery'
        ).publish_json()
        assert json['properties']['meta']['url'] == (
            'http://localhost/live-prefix/video/seo-slug-cookies'
        )

    def test_bigquery_adapters_are_registered(self):
        import zeit.content.article.article
        import zeit.content.cp.centerpage
        import zeit.content.gallery.gallery
        import zeit.content.video.video

        article = zeit.content.article.article.Article()
        assert (
            zope.component.queryAdapter(
                article, zeit.workflow.interfaces.IPublisherData, name='bigquery'
            )
            is not None
        )
        centerpage = zeit.content.cp.centerpage.CenterPage()
        assert (
            zope.component.queryAdapter(
                centerpage, zeit.workflow.interfaces.IPublisherData, name='bigquery'
            )
            is not None
        )
        gallery = zeit.content.gallery.gallery.Gallery()
        assert (
            zope.component.queryAdapter(
                gallery, zeit.workflow.interfaces.IPublisherData, name='bigquery'
            )
            is not None
        )
        video = zeit.content.video.video.Video()
        assert (
            zope.component.queryAdapter(
                video, zeit.workflow.interfaces.IPublisherData, name='bigquery'
            )
            is not None
        )

    def test_comments_are_published(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        self.assertFalse(IPublishInfo(article).published)
        with requests_mock.Mocker() as rmock:
            response = rmock.post('http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            result_comments = result['comments']
            self.assertEqual(
                {
                    'comments_allowed': False,
                    'pre_moderated': False,
                    'type': 'commentsection',
                    'visible': False,
                },
                result_comments,
            )
        self.assertTrue(IPublishInfo(article).published)

    def test_comments_adapters_are_registered(self):
        import zeit.content.article.article
        import zeit.content.gallery.gallery
        import zeit.content.video.video

        article = zeit.content.article.article.Article()
        assert (
            zope.component.queryAdapter(
                article, zeit.workflow.interfaces.IPublisherData, name='comments'
            )
            is not None
        )
        gallery = zeit.content.gallery.gallery.Gallery()
        assert (
            zope.component.queryAdapter(
                gallery, zeit.workflow.interfaces.IPublisherData, name='comments'
            )
            is not None
        )
        video = zeit.content.video.video.Video()
        assert (
            zope.component.queryAdapter(
                video, zeit.workflow.interfaces.IPublisherData, name='comments'
            )
            is not None
        )

    def test_speechbert_is_published(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        self.assertFalse(IPublishInfo(article).published)
        with requests_mock.Mocker() as rmock:
            response = rmock.post('http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            result_sb = result['speechbert']
            self.assertEqual(
                [
                    'body',
                    'checksum',
                    'hasAudio',
                    'headline',
                    'publishDate',
                    'section',
                    'series',
                    'subtitle',
                    'supertitle',
                    'teaser',
                ],
                sorted(result_sb.keys()),
            )
        self.assertTrue(IPublishInfo(article).published)

    def test_speechbert_audiospeechbert(self):
        # TODO: add a test which checks audiospeechbert which should
        # set hasAudio to False to tell speechbert to skip audio generation
        pass

    def test_speechbert_ignore_genres(self):
        article = ICMSContent('http://xml.zeit.de/zeit-magazin/wochenmarkt/rezept')
        zeit.cms.config.set('zeit.workflow', 'speechbert-ignore-genres', 'rezept-vorstellung')
        json = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert json is None
        zeit.cms.config.set('zeit.workflow', 'speechbert-ignore-genres', '')
        json = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert json is not None

    def test_speechbert_ignore_templates(self):
        article = ICMSContent('http://xml.zeit.de/zeit-magazin/wochenmarkt/rezept')
        zeit.cms.config.set('zeit.workflow', 'speechbert-ignore-templates', 'article')
        json = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert json is None
        zeit.cms.config.set('zeit.workflow', 'speechbert-ignore-templates', '')
        json = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert json is not None

    def test_speechbert_ignores_dpa_news(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        json = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert json is not None
        with checked_out(article) as co:
            co.product = zeit.cms.content.sources.Product(
                id='dpaBY', title='DPA Bayern', show='source', is_news=True
            )
        json = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert json is None

    def test_summy_ignore_genre_list(self):
        article = ICMSContent('http://xml.zeit.de/zeit-magazin/wochenmarkt/rezept')
        zeit.cms.config.set('zeit.workflow', 'summy-ignore-genres', 'rezept-vorstellung')
        payload = zeit.workflow.testing.publish_json(article, 'summy')
        assert payload == {}

    def test_summy_ignore_ressort_list(self):
        article = ICMSContent('http://xml.zeit.de/zeit-magazin/wochenmarkt/rezept')
        zeit.cms.config.set('zeit.workflow', 'summy-ignore-ressorts', 'zeit-magazin')
        payload = zeit.workflow.testing.publish_json(article, 'summy')
        assert payload == {}

    def test_summy_payload(self):
        article = ICMSContent('http://xml.zeit.de/zeit-magazin/wochenmarkt/rezept')
        zeit.cms.config.set('zeit.workflow', 'summy-ignore-ressorts', 'valid_ressort')
        zeit.cms.config.set('zeit.workflow', 'summy-ignore-genres', 'valid_genre')
        payload = zeit.workflow.testing.publish_json(article, 'summy')
        parts = payload['text']
        assert parts[0] == {'content': 'Als Beilage passt gedämpfter Brokkoli.', 'type': 'p'}
        assert parts[5] == {'content': '  Rezept von Compliment to the Chef   ', 'type': 'p'}
        assert payload['avoid_create_summary'] is False


class SpeechbertPayloadTest(zeit.workflow.testing.FunctionalTestCase):
    layer = zeit.content.article.testing.LAYER

    def create_author(self, firstname, lastname, key):
        author = zeit.content.author.author.Author()
        author.firstname = firstname
        author.lastname = lastname
        self.repository[key] = author

    @pytest.fixture(autouse=True)
    def _monkeypatch(self, monkeypatch):
        monkeypatch.setattr(zeit.workflow.publish_3rdparty.Speechbert, 'ignore', lambda s, m: False)

    def test_speechbert_payload(self):
        article = ICMSContent('http://xml.zeit.de/zeit-magazin/wochenmarkt/rezept')
        self.create_author('Eva', 'Biringer', 'author')
        with checked_out(article) as co:
            wl = zope.component.getUtility(zeit.cms.tagging.interfaces.IWhitelist)
            co.keywords = (
                wl.get('Testtag'),
                wl.get('Testtag2'),
                wl.get('Testtag3'),
            )
            co.authorships = [co.authorships.create(self.repository['author'])]
            group = create_image_group_with_master_image(
                file_name='http://xml.zeit.de/2016/DSC00109_2.PNG'
            )
            zeit.content.image.interfaces.IImages(co).image = group

        article = ICMSContent('http://xml.zeit.de/zeit-magazin/wochenmarkt/rezept')
        payload = zeit.workflow.testing.publish_json(article, 'speechbert')
        del payload['body']  # not relevant in this test
        assert payload == {
            'access': 'abo',
            'authors': ['Eva Biringer'],
            'channels': 'zeit-magazin essen-trinken',
            'genre': 'rezept-vorstellung',
            'hasAudio': 'true',
            'headline': 'Vier Rezepte für eine Herdplatte',
            'image': 'http://localhost/img-live-prefix/group/',
            'lastModified': '2020-04-14T09:19:59.618155+00:00',
            'publishDate': '2020-04-14T09:19:59.618155+00:00',
            'section': 'zeit-magazin',
            'subsection': 'essen-trinken',
            'subtitle': (
                'Ist genug Brot und Kuchen gebacken, bleibt endlich wieder '
                'Zeit, zu kochen. Mit diesen One-Pot-Gerichten können Sie den '
                'Zuckerschock vom Osterwochenende kontern.'
            ),
            'tags': ['Testtag', 'Testtag2', 'Testtag3'],
            'teaser': (
                'Ist genug Brot und Kuchen gebacken, ' 'bleibt endlich wieder Zeit, zu kochen.'
            ),
        }

    def test_speechbert_payload_access_free(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/weissrussland-russland-gas')
        payload = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert article.access == 'free'
        assert 'access' not in payload

    def test_speechbert_payload_multiple_authors(self):
        article = ICMSContent('http://xml.zeit.de/online/2022/08/kaenguru-comics-folge-448')
        with checked_out(article) as co:
            self.create_author('Marc-Uwe', 'Kling', 'a1')
            self.create_author('Bernd', 'Kissel', 'a2')
            self.create_author('Julian', 'Stahnke', 'a3')
            co.authorships = [
                co.authorships.create(self.repository['a1']),
                co.authorships.create(self.repository['a2']),
                co.authorships.create(self.repository['a3']),
            ]
            co.authorships[2].role = 'Illustration'

        article = ICMSContent('http://xml.zeit.de/online/2022/08/kaenguru-comics-folge-448')
        payload = zeit.workflow.testing.publish_json(article, 'speechbert')
        raw_authors = [(author.target.display_name, author.role) for author in article.authorships]
        assert raw_authors == [
            ('Marc-Uwe Kling', None),
            ('Bernd Kissel', None),
            ('Julian Stahnke', 'Illustration'),
        ]
        assert payload['authors'] == ['Marc-Uwe Kling', 'Bernd Kissel']

    def test_speechbert_payload_no_entry_if_attribute_none(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/weissrussland-russland-gas')
        payload = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert article.channels == ()
        assert 'channels' not in payload

    def test_speechbert_payload_single_channel(self):
        article = ICMSContent('http://xml.zeit.de/online/2022/08/trockenheit')
        payload = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert article.channels == (('News', None),)
        assert payload['channels'] == 'News'

    def test_speechbert_payload_series(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/weissrussland-russland-gas')
        payload = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert article.serie is not None
        assert payload['series'] == '-'

    def test_speechbert_payload_supertitle(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/weissrussland-russland-gas')
        payload = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert article.supertitle == 'Geopolitik'
        assert payload['supertitle'] == 'Geopolitik'

    def test_includes_child_tags_in_body(self):
        article = zeit.content.article.testing.create_article()
        p = article.body.create_item('p')
        p.text = 'before <em>during</em> after'
        article = self.repository['article'] = article
        payload = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert payload['body'] == [{'type': 'p', 'content': 'before during after'}]


class AirshipTest(zeit.workflow.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()

        FEATURE_TOGGLES.set('push_airship_via_publisher')

        # We don't care about the whole zeit.push templating infrastructure here
        self.patch = unittest.mock.patch('zeit.push.urbanairship.Message.render')
        render = self.patch.start()
        render.return_value = [{}]

    def tearDown(self):
        self.patch.stop()
        super().tearDown()

    def test_no_push_configures_skips_task(self):
        content = self.repository['testcontent']
        data = zeit.workflow.testing.publish_json(content, 'airship')
        self.assertEqual(None, data)

        info = zeit.push.interfaces.IPushMessages(content)
        info.message_config = [
            {'type': 'unrelated', 'enabled': True},
            {'type': 'mobile', 'enabled': False},
        ]
        data = zeit.workflow.testing.publish_json(content, 'airship')
        self.assertEqual(None, data)

    def test_delegates_payload_to_message_template(self):
        content = self.repository['testcontent']
        info = zeit.push.interfaces.IPushMessages(content)
        info.message_config = [{'type': 'mobile', 'enabled': True}]
        data = zeit.workflow.testing.publish_json(content, 'airship')
        self.assertEqual(['kind', 'pushes'], list(data.keys()))

    def test_sets_absolute_expiry(self):
        content = self.repository['testcontent']
        info = zeit.push.interfaces.IPushMessages(content)
        info.message_config = [{'type': 'mobile', 'enabled': True}]
        data = zeit.workflow.testing.publish_json(content, 'airship')
        expiry = data['pushes'][0]['options']['expiry']
        with self.assertNothingRaised():
            pendulum.parse(expiry)


class TMSPayloadTest(zeit.workflow.testing.FunctionalTestCase):
    def test_tms_wait_for_index_article(self):
        article = self.repository['testcontent']
        zope.interface.alsoProvides(article, zeit.content.article.interfaces.IArticle)
        data_factory = zope.component.getAdapter(
            article, zeit.workflow.interfaces.IPublisherData, name='tms'
        )
        payload = data_factory.publish_json()
        assert payload == {'wait': True}

    def test_tms_only_waits_for_articles(self):
        content = self.repository['testcontent']
        data_factory = zope.component.getAdapter(
            content, zeit.workflow.interfaces.IPublisherData, name='tms'
        )
        payload = data_factory.publish_json()
        assert payload == {'wait': False}

    def test_tms_ignores_content_without_tms_representation(self):
        content = self.repository['testcontent']
        zeit.workflow.testing.MockTMSRepresentation.result = None
        data_factory = zope.component.getAdapter(
            content, zeit.workflow.interfaces.IPublisherData, name='tms'
        )
        payload = data_factory.publish_json()
        assert payload is None


class BigQueryPayloadTest(zeit.workflow.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        zeit.workflow.testing.MockTMSRepresentation.result = {
            'payload': {'document': {'uuid': '{urn:uuid:myuuid}'}}
        }
        with checked_out(self.repository['testcontent']):
            pass  # XXX trigger uuid generation
        self.article = self.repository['testcontent']
        zope.interface.alsoProvides(self.article, zeit.content.article.interfaces.IArticle)

    def test_includes_uniqueid_under_meta(self):
        data = zope.component.getAdapter(
            self.article, zeit.workflow.interfaces.IPublisherData, name='bigquery'
        )
        for action in ['publish', 'retract']:
            d = getattr(data, f'{action}_json')()
            self.assertEqual(
                'http://localhost/live-prefix/testcontent', d['properties']['meta']['url']
            )
            self.assertStartsWith('{urn:uuid:', d['properties']['document']['uuid'])

    def test_moves_rtr_keywords_under_tagging(self):
        zeit.workflow.testing.MockTMSRepresentation.result = {
            'rtr_locations': [],
            'rtr_keywords': ['one', 'two'],
            'title': 'ignored',
        }
        data = zeit.workflow.testing.publish_json(self.article, 'bigquery')
        self.assertEqual(
            {'rtr_locations': [], 'rtr_keywords': ['one', 'two']}, data['properties']['tagging']
        )

    def test_converts_body_to_badgerfish_json(self):
        # fmt: off
        body_string = """<body>
<division><p>one</p>
<p>two</p>\r  </division>
</body>
"""
        # fmt: on
        self.article.xml.replace(
            self.article.xml.find('body'),
            lxml.etree.fromstring(body_string),
        )
        data = zeit.workflow.testing.publish_json(self.article, 'bigquery')
        self.assertEqual({'division': {'p': [{'$': 'one'}, {'$': 'two'}]}}, data['body'])


class BadgerfishTest(unittest.TestCase):
    def badgerfish(self, text):
        return zeit.workflow.publish_3rdparty.badgerfish(lxml.etree.XML(text))

    def test_text_becomes_dollar(self):
        self.assertEqual({'a': {'$': 'b'}}, self.badgerfish('<a>b</a>'))

    def test_children_become_nested_dict(self):
        self.assertEqual(
            {'a': {'b': {'$': 'c'}, 'd': {'$': 'e'}}}, self.badgerfish('<a><b>c</b><d>e</d></a>')
        )

    def test_children_same_name_become_list(self):
        self.assertEqual(
            {'a': {'b': [{'$': 'c'}, {'$': 'd'}]}}, self.badgerfish('<a><b>c</b><b>d</b></a>')
        )

    def test_attributes_become_prefixed_with_at(self):
        self.assertEqual({'a': {'$': 'b', '@c': 'd'}}, self.badgerfish('<a c="d">b</a>'))

    def test_namespace_is_removed_from_tag(self):
        self.assertEqual({'a': {}}, self.badgerfish('<x:a xmlns:x="x" />'))

    def test_namespace_is_removed_from_attribute(self):
        self.assertEqual({'a': {'@b': 'c'}}, self.badgerfish('<a xmlns:x="x" x:b="c" />'))

    def test_mixed_content_becomes_dollar(self):
        self.assertEqual(
            {'a': {'$': 'before child after'}}, self.badgerfish('<a>before <b>child</b> after</a>')
        )
        self.assertEqual(
            {'a': {'$': 'before child'}}, self.badgerfish('<a>before <b>child</b></a>')
        )
        self.assertEqual({'a': {'$': 'child after'}}, self.badgerfish('<a><b>child</b> after</a>'))

    def test_comment_is_removed(self):
        self.assertEqual({'a': {}}, self.badgerfish('<a><!-- comment --></a>'))
