import unittest

from lxml.builder import E
import lxml.etree
import pendulum
import pytest
import requests_mock
import transaction
import zope.app.appsetup.product
import zope.component
import zope.i18n

from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.interfaces import ICMSContent
from zeit.cms.tagging.tag import Tag
from zeit.cms.workflow.interfaces import IPublish, IPublisher, IPublishInfo
from zeit.content.article.testing import create_article
from zeit.content.image.testing import create_image_group
import zeit.cms.related.interfaces
import zeit.cms.tagging.interfaces
import zeit.cms.testing
import zeit.content.article.article
import zeit.content.audio.audio
import zeit.content.author.author
import zeit.content.cp.centerpage
import zeit.content.gallery.gallery
import zeit.content.video.video
import zeit.objectlog.interfaces
import zeit.workflow.interfaces
import zeit.workflow.publish
import zeit.workflow.publish_3rdparty
import zeit.workflow.publisher
import zeit.workflow.testing


class Publisher3rdPartyTest(zeit.workflow.testing.FunctionalTestCase):
    layer = zeit.workflow.testing.CONTENT_LAYER

    def setUp(self):
        super().setUp()
        self.gsm = zope.component.getGlobalSiteManager()
        self.gsm.registerUtility(zeit.workflow.publisher.Publisher(), IPublisher)
        self.repository['article'] = create_article()
        transaction.commit()

    @pytest.fixture(autouse=True)
    def _caplog(self, caplog):
        self.caplog = caplog

    def test_ignore_3rdparty_list_is_respected(self):
        article = self.repository['article']
        self.assertFalse(IPublishInfo(article).published)
        IPublishInfo(article).urgent = True
        zeit.workflow.publish_3rdparty.PublisherData.ignore = ['speechbert']
        with requests_mock.Mocker() as rmock:
            response = rmock.post('http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=True)
            (result,) = response.last_request.json()
            assert 'speechbert' not in result
            assert 'indexnow' in result

            FEATURE_TOGGLES.set('disable_publisher_indexnow')
            response = rmock.post('http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            assert 'speechbert' not in result
            assert 'indexnow' not in result
        zeit.workflow.publish_3rdparty.PublisherData.ignore = []  # reset
        self.assertTrue(IPublishInfo(article).published)

    def test_bigquery_is_published(self):
        article = self.repository['article']
        self.assertFalse(IPublishInfo(article).published)
        IPublishInfo(article).urgent = True
        with requests_mock.Mocker() as rmock:
            response = rmock.post('http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            result_bq = result['bigquery']
            self.assertEqual(
                'http://localhost/live-prefix/article',
                result_bq['properties']['meta']['url'],
            )
        self.assertTrue(IPublishInfo(article).published)

    def test_video_contains_seo_slug_in_url(self):
        video = zeit.content.video.video.Video()
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
        audio = zeit.content.audio.audio.Audio()
        assert (
            zope.component.queryAdapter(
                audio, zeit.workflow.interfaces.IPublisherData, name='bigquery'
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

    def test_datascience_adapters_are_registered(self):
        adapters = [
            zeit.content.article.article.Article(),
            zeit.content.cp.centerpage.CenterPage(),
            zeit.content.gallery.gallery.Gallery(),
            zeit.content.video.video.Video(),
            zeit.content.audio.audio.Audio(),
            zeit.content.author.author.Author(),
        ]
        for adapter in adapters:
            assert (
                zope.component.queryAdapter(
                    adapter, zeit.workflow.interfaces.IPublisherData, name='datascience'
                )
                is not None
            )

    def test_comments_are_published(self):
        with checked_out(self.repository['article']) as co:
            co.commentSectionEnable = False
            co.commentsAllowed = False
        transaction.commit()
        article = self.repository['article']
        self.assertFalse(IPublishInfo(article).published)
        IPublishInfo(article).urgent = True
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
        article = self.repository['article']
        self.assertFalse(IPublishInfo(article).published)
        IPublishInfo(article).urgent = True
        with requests_mock.Mocker() as rmock:
            response = rmock.post('http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            result_sb = result['speechbert']
            self.assertEqual(
                [
                    'checksum',
                    'hasAudio',
                    'headline',
                    'lastModified',
                    'publishDate',
                    'section',
                ],
                sorted(result_sb.keys()),
            )
        self.assertTrue(IPublishInfo(article).published)

    def test_speechbert_audio_speechbert_is_false(self):
        article = self.repository['article']
        json = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert json is not None
        with checked_out(article) as co:
            co.audio_speechbert = False
        json = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert json is None

    def test_speechbert_ignore_genres(self):
        zeit.cms.config.set('zeit.workflow', 'speechbert-ignore-genres', 'rezept-vorstellung')
        article = self.repository['article']
        with checked_out(article) as co:
            co.genre = 'rezept-vorstellung'
        transaction.commit()
        json = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert json is None
        zeit.cms.config.set('zeit.workflow', 'speechbert-ignore-genres', '')
        json = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert json is not None

    def test_speechbert_ignore_templates(self):
        zeit.cms.config.set('zeit.workflow', 'speechbert-ignore-templates', 'article')
        article = self.repository['article']
        with checked_out(article) as co:
            co.template = 'article'
        transaction.commit()
        json = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert json is None
        zeit.cms.config.set('zeit.workflow', 'speechbert-ignore-templates', '')
        json = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert json is not None

    def test_speechbert_ignores_dpa_news(self):
        article = self.repository['article']
        json = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert json is not None
        with checked_out(article) as co:
            co.ressort = 'News'
        transaction.commit()
        zeit.cms.config.set('zeit.workflow', 'speechbert-ignore-ressorts', 'news')
        json = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert json is None

    def test_summy_ignore_genre_list(self):
        zeit.cms.config.set('zeit.workflow', 'summy-ignore-genres', 'rezept-vorstellung')
        article = self.repository['article']
        with checked_out(article) as co:
            co.genre = 'rezept-vorstellung'
        transaction.commit()
        payload = zeit.workflow.testing.publish_json(article, 'summy')
        assert payload == {}

    def test_summy_ignore_ressort_list(self):
        zeit.cms.config.set('zeit.workflow', 'summy-ignore-ressorts', 'zeit-magazin')
        article = self.repository['article']
        with checked_out(article) as co:
            co.ressort = 'zeit-magazin'
        transaction.commit()
        payload = zeit.workflow.testing.publish_json(article, 'summy')
        assert payload == {}

    def test_summy_ignore_products_list(self):
        article = self.repository['article']
        payload = zeit.workflow.testing.publish_json(article, 'summy')
        assert payload != {}

        zeit.cms.config.set('zeit.workflow', 'summy-ignore-products', 'dpaBY')
        with checked_out(article) as co:
            co.product = (
                zeit.cms.content.interfaces.ICommonMetadata['product'].source(co).find('dpaBY')
            )
        transaction.commit()
        payload = zeit.workflow.testing.publish_json(article, 'summy')
        assert payload == {}

    def test_summy_payload(self):
        article = ICMSContent('http://xml.zeit.de/article')
        article.xml.find('body').append(E.division(E.p('Beispieltext')))
        payload = zeit.workflow.testing.publish_json(article, 'summy')
        parts = payload['text']
        assert parts[0] == {'content': 'Beispieltext', 'type': 'p'}
        assert payload['avoid_create_summary'] is False


class SpeechbertPayloadTest(zeit.workflow.testing.FunctionalTestCase):
    layer = zeit.workflow.testing.CONTENT_LAYER

    def setUp(self):
        super().setUp()
        self.repository['article'] = create_article()
        transaction.commit()

    def create_author(self, firstname, lastname, key):
        author = zeit.content.author.author.Author()
        author.firstname = firstname
        author.lastname = lastname
        self.repository[key] = author

    @pytest.fixture(autouse=True)
    def _monkeypatch(self, monkeypatch):
        monkeypatch.setattr(zeit.workflow.publish_3rdparty.Speechbert, 'ignore', lambda self: False)

    def test_speechbert_payload(self):
        self.create_author('Eva', 'Biringer', 'author')
        with checked_out(self.repository['article']) as co:
            co.ressort = 'zeit-magazin'
            co.sub_ressort = 'essen-trinken'
            co.access = 'abo'
            wl = zope.component.getUtility(zeit.cms.tagging.interfaces.IWhitelist)
            co.keywords = (
                wl.get('Testtag'),
                wl.get('Testtag2'),
                wl.get('Testtag3'),
            )
            co.authorships = [co.authorships.create(self.repository['author'])]
            group = create_image_group()
            zeit.content.image.interfaces.IImages(co).image = group

        article = self.repository['article']
        payload = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert payload == {
            'access': 'abo',
            'authors': ['Eva Biringer'],
            'hasAudio': 'true',
            'headline': 'title',
            'image': 'http://localhost/img-live-prefix/group/',
            'section': 'zeit-magazin',
            'subsection': 'essen-trinken',
            'tags': ['Testtag', 'Testtag2', 'Testtag3'],
        }

    def test_speechbert_payload_access_free(self):
        with checked_out(self.repository['article']) as co:
            co.access = 'free'
        transaction.commit()
        article = self.repository['article']
        payload = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert article.access == 'free'
        assert 'access' not in payload

    def test_speechbert_payload_multiple_authors(self):
        with checked_out(self.repository['article']) as co:
            self.create_author('Marc-Uwe', 'Kling', 'a1')
            self.create_author('Bernd', 'Kissel', 'a2')
            self.create_author('Julian', 'Stahnke', 'a3')
            co.authorships = [
                co.authorships.create(self.repository['a1']),
                co.authorships.create(self.repository['a2']),
                co.authorships.create(self.repository['a3']),
            ]
            co.authorships[2].role = 'Illustration'
        transaction.commit()
        article = self.repository['article']
        payload = zeit.workflow.testing.publish_json(article, 'speechbert')
        raw_authors = [(author.target.display_name, author.role) for author in article.authorships]
        assert raw_authors == [
            ('Marc-Uwe Kling', None),
            ('Bernd Kissel', None),
            ('Julian Stahnke', 'Illustration'),
        ]
        assert payload['authors'] == ['Marc-Uwe Kling', 'Bernd Kissel']

    def test_speechbert_payload_no_entry_if_attribute_none(self):
        article = self.repository['article']
        payload = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert article.channels == ()
        assert 'channels' not in payload

    def test_speechbert_payload_single_channel(self):
        with checked_out(self.repository['article']) as co:
            co.channels = (('Wissen', None),)
        transaction.commit()
        article = self.repository['article']
        payload = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert payload['channels'] == 'Wissen'

    def test_speechbert_payload_series(self):
        article = self.repository['article']
        with checked_out(article) as co:
            co.serie = 'Geschafft!'
        transaction.commit()
        payload = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert payload['series'] == 'Geschafft!'

    def test_speechbert_payload_supertitle(self):
        with checked_out(self.repository['article']) as co:
            co.supertitle = 'Geopolitik'
        transaction.commit()
        article = self.repository['article']
        payload = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert payload['supertitle'] == 'Geopolitik'

    def test_includes_child_tags_in_body(self):
        article = create_article()
        p = article.body.create_item('p')
        p.text = 'before <em>during</em> after'
        article = self.repository['article'] = article
        payload = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert payload['body'] == [{'type': 'p', 'content': 'before during after'}]


class AirshipTest(zeit.workflow.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
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
    layer = zeit.workflow.testing.CONTENT_LAYER

    def test_tms_wait_for_index_article(self):
        self.repository['article'] = create_article()
        data_factory = zope.component.getAdapter(
            self.repository['article'], zeit.workflow.interfaces.IPublisherData, name='tms'
        )
        payload = data_factory.publish_json()
        assert payload == {'wait': True}

    def test_tms_only_waits_for_articles(self):
        content = zeit.content.cp.centerpage.CenterPage()
        content.title = 'test'
        self.repository['cp'] = content
        content = self.repository['cp']

        data_factory = zope.component.getAdapter(
            content, zeit.workflow.interfaces.IPublisherData, name='tms'
        )
        payload = data_factory.publish_json()
        assert payload == {'wait': False}

    def test_tms_ignores_content_without_tms_representation(self):
        content = self.repository['testcontent']
        # Fake a known content type, so IPublisherData picks it up.
        zope.interface.alsoProvides(content, zeit.content.cp.interfaces.ICenterPage)
        data_factory = zope.component.getAdapter(
            content, zeit.workflow.interfaces.IPublisherData, name='tms'
        )
        payload = data_factory.publish_json()
        assert payload is None


class BigQueryPayloadTest(zeit.workflow.testing.FunctionalTestCase):
    layer = zeit.workflow.testing.CONTENT_LAYER

    def setUp(self):
        super().setUp()
        self.repository['article'] = create_article()
        transaction.commit()

    def test_includes_uniqueid_under_meta(self):
        data = zope.component.getAdapter(
            self.repository['article'], zeit.workflow.interfaces.IPublisherData, name='bigquery'
        )
        for action in ['publish', 'retract']:
            d = getattr(data, f'{action}_json')()
            self.assertEqual(
                'http://localhost/live-prefix/article',
                d['properties']['meta']['url'],
            )
            self.assertStartsWith('{urn:uuid:', d['properties']['document']['uuid'])

    def test_moves_rtr_keywords_under_tagging(self):
        article = self.repository['article']
        with checked_out(article) as co:
            co.keywords = (Tag('Hannover', 'location'), Tag('Paris', 'location'))

        data = zeit.workflow.testing.publish_json(article, 'bigquery')
        self.assertEqual(['Hannover', 'Paris'], data['properties']['tagging']['rtr_locations'])

    def test_converts_body_to_badgerfish_json(self):
        # fmt: off
        body_string = """<body>
<division><p>one</p>
<p>two</p>\r  </division>
</body>
"""
        # fmt: on
        article = self.repository['article']
        article.xml.replace(
            article.xml.find('body'),
            lxml.etree.fromstring(body_string),
        )
        data = zeit.workflow.testing.publish_json(article, 'bigquery')
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


class IndexNowPayloadTest(zeit.workflow.testing.FunctionalTestCase):
    def test_index_now_payload_article(self):
        article = self.repository['testcontent']
        zope.interface.alsoProvides(article, zeit.content.article.interfaces.IArticle)
        data = zeit.workflow.testing.publish_json(article, 'indexnow')
        self.assertEqual('http://localhost/live-prefix/testcontent', data['url'])

    def test_index_now_payload_centerpage(self):
        article = self.repository['testcontent']
        zope.interface.alsoProvides(article, zeit.content.cp.interfaces.ICenterPage)
        data = zeit.workflow.testing.publish_json(article, 'indexnow')
        self.assertEqual('http://localhost/live-prefix/testcontent', data['url'])


class DatasciencePayloadTest(zeit.workflow.testing.FunctionalTestCase):
    layer = zeit.workflow.testing.CONTENT_LAYER

    def test_datascience_payload_article(self):
        article = zeit.content.article.testing.create_article()
        p = article.body.create_item('p')
        p.text = 'foo'
        article = self.repository['article'] = article
        payload = zeit.workflow.testing.publish_json(article, 'datascience')
        self.assertEqual(payload['body'], lxml.etree.tostring(article.xml, encoding=str))

    def test_datascience_payload_ignore_article(self):
        article = zeit.content.article.testing.create_article()
        zeit.cms.config.set(
            'zeit.workflow',
            'datascience-ignore-uniqueids',
            'http://xml.zeit.de/article http://xml.zeit.de/article-two',
        )
        p = article.body.create_item('p')
        p.text = 'foo'
        article = self.repository['article'] = article
        payload = zeit.workflow.testing.publish_json(article, 'datascience')
        self.assertEqual(payload, None)

    def test_datascience_payload_centerpage(self):
        cp = zeit.content.cp.centerpage.CenterPage()
        self.repository['cp'] = cp
        cp = self.repository['cp']
        data = zeit.workflow.testing.publish_json(cp, 'datascience')
        self.assertEqual(data['body'], lxml.etree.tostring(cp.xml, encoding=str))

    def test_datascience_payload_gallery(self):
        gallery = zeit.content.gallery.gallery.Gallery()
        self.repository['gallery'] = gallery
        gallery = self.repository['gallery']
        data = zeit.workflow.testing.publish_json(gallery, 'datascience')
        self.assertEqual(data['body'], lxml.etree.tostring(gallery.xml, encoding=str))

    def test_datascience_payload_author(self):
        author = zeit.content.author.author.Author()
        author.uniqueId = 'http://xml.zeit.de/author'
        author.firstname = 'Hans'
        author.lastname = 'Wurst'
        data = zeit.workflow.testing.publish_json(author, 'datascience')
        self.assertEqual(data['body'], lxml.etree.tostring(author.xml, encoding=str))

    def test_datascience_payload_audio(self):
        from zeit.content.audio.testing import AudioBuilder

        audio = AudioBuilder().build()
        audio = self.repository['audio'] = audio
        data = zeit.workflow.testing.publish_json(audio, 'datascience')
        self.assertEqual(data['body'], lxml.etree.tostring(audio.xml, encoding=str))

    def test_datascience_payload_video(self):
        from zeit.content.video.testing import video_factory

        video = next(video_factory(self))
        video = self.repository['video'] = video
        data = zeit.workflow.testing.publish_json(video, 'datascience')
        self.assertEqual(data['body'], lxml.etree.tostring(video.xml, encoding=str))


class FollowingsPayloadTest(zeit.workflow.testing.FunctionalTestCase):
    layer = zeit.workflow.testing.CONTENT_LAYER

    def setUp(self):
        super().setUp()
        self.repository['article'] = create_article()
        IPublishInfo(self.repository['article']).date_first_released = pendulum.datetime(
            2025, 7, 20
        )
        self.repository['serie'] = zeit.cms.repository.folder.Folder()
        self.repository['serie']['chefsache'] = zeit.content.cp.centerpage.CenterPage()
        transaction.commit()
        self.cp = self.repository['serie']['chefsache']

    def test_followings_podcast(self):
        from zeit.content.audio.testing import AudioBuilder

        audio = AudioBuilder().with_audio_type('podcast').build()
        audio = self.repository['audio'] = audio
        with checked_out(self.repository['article']) as co:
            co.serie = 'Chefsache'
            audios_refs = zeit.content.audio.interfaces.IAudioReferences(co)
            audios_refs.add(audio)
        transaction.commit()
        expected_uuid = zeit.cms.content.interfaces.IUUID(self.cp).shortened

        data = zeit.workflow.testing.publish_json(self.repository['article'], 'followings')
        self.assertEqual(data['parent_uuids'][0], expected_uuid)
        self.assertEqual(data['created'], '2025-07-20T00:00:00+00:00')

    def test_followings_series(self):
        with checked_out(self.repository['article']) as co:
            co.serie = 'Chefsache'
        expected_uuid = zeit.cms.content.interfaces.IUUID(self.cp).shortened
        data = zeit.workflow.testing.publish_json(self.repository['article'], 'followings')
        self.assertEqual(data['parent_uuids'][0], expected_uuid)

    def test_followings_author(self):
        author = zeit.content.author.author.Author()
        author.firstname = 'Mark-Uwe'
        author.lastname = 'Kling'
        self.repository['author'] = author
        with checked_out(self.repository['article']) as co:
            co.authorships = [co.authorships.create(self.repository['author'])]
        transaction.commit()
        expected_uuid = zeit.cms.content.interfaces.IUUID(self.repository['author']).shortened
        data = zeit.workflow.testing.publish_json(self.repository['article'], 'followings')
        self.assertEqual(data['parent_uuids'][0], expected_uuid)

    def test_followings_series_author_combination(self):
        author = zeit.content.author.author.Author()
        author.firstname = 'Mark-Uwe'
        author.lastname = 'Kling'
        self.repository['author'] = author
        transaction.commit()
        with checked_out(self.repository['article']) as co:
            co.serie = 'Chefsache'
            co.authorships = [co.authorships.create(self.repository['author'])]
        transaction.commit()

        expected_series_uuid = zeit.cms.content.interfaces.IUUID(self.cp).shortened
        expected_author_uuid = zeit.cms.content.interfaces.IUUID(
            self.repository['author']
        ).shortened

        data = zeit.workflow.testing.publish_json(self.repository['article'], 'followings')
        self.assertEqual(
            sorted(data['parent_uuids']), sorted([expected_author_uuid, expected_series_uuid])
        )

    def test_followings_recipe_categories(self):
        with checked_out(self.repository['article']) as co:
            co.genre = 'rezept'

        self.repository['rezepte'] = zeit.cms.repository.folder.Folder()
        self.repository['rezepte']['herbst'] = zeit.content.cp.centerpage.CenterPage()
        transaction.commit()
        article = self.repository['article']
        cp = self.repository['rezepte']['herbst']

        mock_category = unittest.mock.Mock()
        mock_category.id = 'herbst'

        mock_recipe = unittest.mock.Mock()
        mock_recipe.categories = [mock_category]

        with unittest.mock.patch('zeit.workflow.publish_3rdparty.IRecipeArticle') as mock_adapter:
            mock_adapter.return_value = mock_recipe

            expected_uuid = zeit.cms.content.interfaces.IUUID(cp).shortened

            data = zeit.workflow.testing.publish_json(article, 'followings')
            self.assertIsNotNone(data, 'Data should not be None when recipe categories are present')
            self.assertEqual(data['parent_uuids'][0], expected_uuid)

    def test_followings_volume(self):
        self.repository['data'] = zeit.cms.repository.folder.Folder()
        volume_uuid = '2742c390-8618-480c-aa89-173907456a64'
        volume_audio_uuid = '18ba93e7-54a4-4cc4-8c76-05ee063382db'
        self.repository['2025'] = zeit.cms.repository.folder.Folder()
        self.repository['2025']['10'] = zeit.cms.repository.folder.Folder()
        cp = self.repository['2025']['10']['index'] = zeit.content.cp.centerpage.CenterPage()
        self.repository['index'] = zeit.content.cp.centerpage.CenterPage()
        zope.interface.alsoProvides(cp, zeit.content.volume.interfaces.IVolume)

        with checked_out(cp):
            cp.year = 2025
            cp.volume = 10
            cp.type = 'volume'
            info = zeit.cms.workflow.interfaces.IPublishInfo(cp)
            info.date_first_released = pendulum.datetime(2025, 3, 5, 8, 18)

        data = zeit.workflow.testing.publish_json(cp, 'followings')
        date = zeit.cms.workflow.interfaces.IPublishInfo(cp).date_first_released
        self.assertIsNotNone(data, 'Data should not be None')
        self.assertEqual(len(data['parent_uuids']), 2)
        self.assertTrue(volume_uuid in data['parent_uuids'])
        self.assertTrue(volume_audio_uuid in data['parent_uuids'])
        self.assertEqual(data['created'], date.isoformat())

    def test_followings_volume_wochenende(self):
        self.repository['wochenende'] = zeit.cms.repository.folder.Folder()
        self.repository['wochenende']['2025'] = zeit.cms.repository.folder.Folder()
        cp = self.repository['wochenende']['2025']['10'] = zeit.content.cp.centerpage.CenterPage()
        zope.interface.alsoProvides(cp, zeit.wochenende.interfaces.IZWEContent)
        expected_uuid = '31ac2c26-2061-440f-946c-71532a322624'

        with checked_out(cp):
            info = zeit.cms.workflow.interfaces.IPublishInfo(cp)
            info.date_first_released = pendulum.datetime(2025, 3, 5, 8, 18)

        data = zeit.workflow.testing.publish_json(cp, 'followings')
        date = zeit.cms.workflow.interfaces.IPublishInfo(cp).date_first_released
        self.assertIsNotNone(data, 'Data should not be None')
        self.assertEqual(data['parent_uuids'][0], expected_uuid)
        self.assertEqual(data['created'], date.isoformat())

    def test_followings_no_series(self):
        data = zeit.workflow.testing.publish_json(self.repository['article'], 'followings')
        self.assertEqual(data, None)
