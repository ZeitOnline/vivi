from unittest import mock
from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.interfaces import ICMSContent
from zeit.cms.workflow.interfaces import IPublishInfo, IPublish, IPublisher
from zeit.content.image.testing import create_image_group_with_master_image
import lxml.etree
import pytest
import requests_mock
import unittest
import zeit.cms.related.interfaces
import zeit.cms.tagging.tag
import zeit.cms.tagging.testing
import zeit.cms.testing
import zeit.content.article.testing
import zeit.content.author.author
import zeit.objectlog.interfaces
import zeit.workflow.interfaces
import zeit.workflow.publish
import zeit.workflow.publish_3rdparty
import zeit.workflow.publisher
import zeit.workflow.testing
import zope.app.appsetup.product
import zope.component
import zope.i18n


class Publisher3rdPartyTest(zeit.workflow.testing.FunctionalTestCase):

    layer = zeit.content.article.testing.LAYER

    def setUp(self):
        self.patch = mock.patch('zeit.retresco.interfaces.ITMSRepresentation')
        self.representation = self.patch.start()
        super().setUp()
        self.gsm = zope.component.getGlobalSiteManager()
        self.gsm.registerUtility(zeit.workflow.publisher.Publisher(),
                                 IPublisher)

    def tearDown(self):
        self.patch.stop()

    @pytest.fixture(autouse=True)
    def _caplog(self, caplog):
        self.caplog = caplog

    def test_ignore_3rdparty_list_is_respected(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).urgent = True
        self.assertFalse(IPublishInfo(article).published)
        article_2 = ICMSContent('http://xml.zeit.de/online/2007/01/Schrempp')
        IPublishInfo(article_2).urgent = True
        IPublishInfo(article_2).published = True
        self.assertTrue(IPublishInfo(article_2).published)
        with requests_mock.Mocker() as rmock:
            zeit.workflow.publish_3rdparty.PublisherData.ignore = [
                'speechbert', 'facebooknewstab']
            response = rmock.post(
                'http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=True)
            (result,) = response.last_request.json()
            assert 'facebooknewstab' not in result
            assert 'speechbert' not in result
            assert 'authordashboard' in result
            zeit.workflow.publish_3rdparty.PublisherData.ignore = [
                'speechbert']
            response = rmock.post(
                'http://localhost:8060/test/publish', status_code=200)
            IPublish(article_2).publish(background=False)
            (result,) = response.last_request.json()
            assert 'speechbert' not in result
            assert 'facebooknewstab' in result
            assert 'authordashboard' in result
        zeit.workflow.publish_3rdparty.PublisherData.ignore = []  # reset
        self.assertTrue(IPublishInfo(article).published)
        self.assertTrue(IPublishInfo(article_2).published)

    def test_authordashboard_is_notified(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).urgent = True
        self.assertFalse(IPublishInfo(article).published)
        with requests_mock.Mocker() as rmock:
            response = rmock.post(
                'http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            result_authordashboard = result['authordashboard']
            self.assertEqual({}, result_authordashboard)
        self.assertTrue(IPublishInfo(article).published)

    def test_bigquery_is_published(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).urgent = True
        self.assertFalse(IPublishInfo(article).published)
        with requests_mock.Mocker() as rmock:
            response = rmock.post(
                'http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            result_bq = result['bigquery']
            self.assertEqual(
                {},
                result_bq)
        self.assertTrue(IPublishInfo(article).published)

    def test_bigquery_adapters_are_registered(self):
        import zeit.content.article.article
        import zeit.content.cp.centerpage
        import zeit.content.gallery.gallery
        import zeit.content.video.video
        article = zeit.content.article.article.Article()
        assert zope.component.queryAdapter(
            article, zeit.workflow.interfaces.IPublisherData,
            name="bigquery") is not None
        centerpage = zeit.content.cp.centerpage.CenterPage()
        assert zope.component.queryAdapter(
            centerpage, zeit.workflow.interfaces.IPublisherData,
            name="bigquery") is not None
        gallery = zeit.content.gallery.gallery.Gallery()
        assert zope.component.queryAdapter(
            gallery, zeit.workflow.interfaces.IPublisherData,
            name="bigquery") is not None
        video = zeit.content.video.video.Video()
        assert zope.component.queryAdapter(
            video, zeit.workflow.interfaces.IPublisherData,
            name="bigquery") is not None

    def test_comments_are_published(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).urgent = True
        self.assertFalse(IPublishInfo(article).published)
        with requests_mock.Mocker() as rmock:
            response = rmock.post(
                'http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            result_comments = result['comments']
            self.assertEqual({
                'comments_allowed': False,
                'pre_moderated': False,
                'type': 'commentsection',
                'visible': False}, result_comments)
        self.assertTrue(IPublishInfo(article).published)

    def test_comments_adapters_are_registered(self):
        import zeit.content.article.article
        import zeit.content.gallery.gallery
        import zeit.content.video.video
        article = zeit.content.article.article.Article()
        assert zope.component.queryAdapter(
            article, zeit.workflow.interfaces.IPublisherData,
            name="comments") is not None
        gallery = zeit.content.gallery.gallery.Gallery()
        assert zope.component.queryAdapter(
            gallery, zeit.workflow.interfaces.IPublisherData,
            name="comments") is not None
        video = zeit.content.video.video.Video()
        assert zope.component.queryAdapter(
            video, zeit.workflow.interfaces.IPublisherData,
            name="comments") is not None

    def test_facebooknewstab_is_published(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).urgent = True
        self.assertFalse(IPublishInfo(article).published)
        with requests_mock.Mocker() as rmock:
            response = rmock.post(
                'http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            result_fbnt = result['facebooknewstab']
            self.assertEqual(
                {},
                result_fbnt)
        self.assertTrue(IPublishInfo(article).published)

    def test_facebooknewstab_skipped_date_first_released(self):
        # this article has date_first_published set to an old date
        article = ICMSContent(
            'http://xml.zeit.de/zeit-magazin/wochenmarkt/rezept')
        IPublishInfo(article).urgent = True
        self.assertTrue(IPublishInfo(article).published)
        self.assertEqual(IPublishInfo(article).date_first_released.year, 2020)
        with requests_mock.Mocker() as rmock:
            response = rmock.post(
                'http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            assert 'facebooknewstab' not in result
        # set it to something else and make sure nothing else caused the skip
        info = IPublishInfo(article)
        info.date_first_released = info.date_first_released.replace(
            year=2022)
        self.assertEqual(IPublishInfo(article).date_first_released.year, 2022)
        with requests_mock.Mocker() as rmock:
            response = rmock.post(
                'http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            assert 'facebooknewstab' in result

    def test_facebooknewstab_skipped_product_id(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).urgent = True
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        self.assertFalse(IPublishInfo(article).published)
        self.assertEqual(article.product.id, "ZEDE")
        # we add more products than needed for the test to make sure
        # the config parsing works correctly
        config['facebooknewstab-ignore-products'] = "ADV, VAB, ZEDE"
        with requests_mock.Mocker() as rmock:
            response = rmock.post(
                'http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            assert 'facebooknewstab' not in result
        # set it to something else and make sure nothing else caused the skip
        with checked_out(article) as co:
            co.product = zeit.cms.content.sources.Product("ZTGS")
        self.assertEqual(article.product.id, "ZTGS")
        with requests_mock.Mocker() as rmock:
            response = rmock.post(
                'http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            assert 'facebooknewstab' in result

    def test_facebooknewstab_skipped_ressort(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).urgent = True
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        self.assertFalse(IPublishInfo(article).published)
        self.assertEqual(article.ressort, "International")
        # we add more products than needed for the test to make sure
        # the config parsing works correctly, that is also why there is
        # a space in front of International
        config['facebooknewstab-ignore-ressorts'] = ",".join([
            "Administratives", " International"])
        with requests_mock.Mocker() as rmock:
            response = rmock.post(
                'http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            assert 'facebooknewstab' not in result
        # set it to something else and make sure nothing else caused the skip
        with checked_out(article) as co:
            co.ressort = "Politik"
        self.assertEqual(article.ressort, "Politik")
        with requests_mock.Mocker() as rmock:
            response = rmock.post(
                'http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            assert 'facebooknewstab' in result

    def test_speechbert_is_published(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).urgent = True
        self.assertFalse(IPublishInfo(article).published)
        with requests_mock.Mocker() as rmock:
            response = rmock.post(
                'http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            result_sb = result['speechbert']
            self.assertEqual(
                ['body', 'checksum', 'hasAudio', 'headline', 'publishDate',
                 'section', 'series', 'subtitle', 'supertitle', 'tags',
                 'teaser'],
                sorted(result_sb.keys()))
        self.assertTrue(IPublishInfo(article).published)

    def test_speechbert_audiospeechbert(self):
        # TODO: add a test which checks audiospeechbert which should
        # set hasAudio to False to tell speechbert to skip audio generation
        pass

    def test_speechbert_ignore_genres(self):
        article = ICMSContent(
            'http://xml.zeit.de/zeit-magazin/wochenmarkt/rezept')
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        config['speechbert-ignore-genres'] = 'rezept-vorstellung'
        json = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert json is None
        config['speechbert-ignore-genres'] = ''
        json = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert json is not None

    def test_speechbert_ignore_templates(self):
        article = ICMSContent(
            'http://xml.zeit.de/zeit-magazin/wochenmarkt/rezept')
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        config['speechbert-ignore-templates'] = 'article'
        json = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert json is None
        config['speechbert-ignore-templates'] = ''
        json = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert json is not None

    def test_speechbert_ignores_dpa_news(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        json = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert json is not None
        with checked_out(article) as co:
            co.product = zeit.cms.content.sources.Product(
                id='dpaBY',
                title='DPA Bayern',
                show='source',
                is_news=True)
        json = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert json is None


class SpeechbertPayloadTest(zeit.workflow.testing.FunctionalTestCase):

    layer = zeit.content.article.testing.LAYER

    def create_author(self, firstname, lastname, key):
        author = zeit.content.author.author.Author()
        author.firstname = firstname
        author.lastname = lastname
        self.repository[key] = author

    @pytest.fixture(autouse=True)
    def _monkeypatch(self, monkeypatch):
        monkeypatch.setattr(
            zeit.workflow.publish_3rdparty.Speechbert,
            'ignore',
            lambda s, m: False)

    def test_speechbert_payload(self):
        article = ICMSContent(
            'http://xml.zeit.de/zeit-magazin/wochenmarkt/rezept')
        self.create_author('Eva', 'Biringer', 'author')
        with checked_out(article) as co:
            wl = zope.component.getUtility(zeit.cms.tagging.interfaces.IWhitelist)
            co.keywords = (
                wl.get('Testtag'), wl.get('Testtag2'), wl.get('Testtag3'),)
            co.authorships = [co.authorships.create(self.repository['author'])]
            group = create_image_group_with_master_image(
                file_name='http://xml.zeit.de/2016/DSC00109_2.PNG')
            zeit.content.image.interfaces.IImages(co).image = group

        article = ICMSContent(
            'http://xml.zeit.de/zeit-magazin/wochenmarkt/rezept')
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
                'Zuckerschock vom Osterwochenende kontern.'),
            'tags': ['Testtag', 'Testtag2', 'Testtag3'],
            'teaser': (
                'Ist genug Brot und Kuchen gebacken, '
                'bleibt endlich wieder Zeit, zu kochen.')}

    def test_speechbert_payload_access_free(self):
        article = ICMSContent(
            'http://xml.zeit.de/online/2007/01/weissrussland-russland-gas')
        payload = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert article.access == 'free'
        assert 'access' not in payload

    def test_speechbert_payload_multiple_authors(self):
        article = ICMSContent(
            'http://xml.zeit.de/online/2022/08/kaenguru-comics-folge-448')
        with checked_out(article) as co:
            self.create_author('Marc-Uwe', 'Kling', 'a1')
            self.create_author('Bernd', 'Kissel', 'a2')
            self.create_author('Julian', 'Stahnke', 'a3')
            co.authorships = [
                co.authorships.create(self.repository['a1']),
                co.authorships.create(self.repository['a2']),
                co.authorships.create(self.repository['a3'])]
            co.authorships[2].role = 'Illustration'

        article = ICMSContent(
            'http://xml.zeit.de/online/2022/08/kaenguru-comics-folge-448')
        payload = zeit.workflow.testing.publish_json(article, 'speechbert')
        raw_authors = [(
            author.target.display_name, author.role)
            for author in article.authorships]
        assert raw_authors == [
            ('Marc-Uwe Kling', None),
            ('Bernd Kissel', None),
            ('Julian Stahnke', 'Illustration')]
        assert payload['authors'] == [
            'Marc-Uwe Kling',
            'Bernd Kissel']

    def test_speechbert_payload_no_entry_if_attribute_none(self):
        article = ICMSContent(
            'http://xml.zeit.de/online/2007/01/weissrussland-russland-gas')
        payload = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert article.channels == ()
        assert 'channels' not in payload

    def test_speechbert_payload_single_channel(self):
        article = ICMSContent(
            'http://xml.zeit.de/online/2022/08/trockenheit')
        payload = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert article.channels == (('News', None),)
        assert payload['channels'] == 'News'

    def test_speechbert_payload_series(self):
        article = ICMSContent(
            'http://xml.zeit.de/online/2007/01/weissrussland-russland-gas')
        payload = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert article.serie is not None
        assert payload['series'] == '-'

    def test_speechbert_payload_supertitle(self):
        article = ICMSContent(
            'http://xml.zeit.de/online/2007/01/weissrussland-russland-gas')
        payload = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert article.supertitle == 'Geopolitik'
        assert payload['supertitle'] == 'Geopolitik'

    def test_includes_child_tags_in_body(self):
        article = zeit.content.article.testing.create_article()
        p = article.body.create_item('p')
        p.text = 'before <em>during</em> after'
        article = self.repository['article'] = article
        payload = zeit.workflow.testing.publish_json(article, 'speechbert')
        assert payload['body'] == [
            {'type': 'p', 'content': 'before during after'}]


class TMSPayloadTest(zeit.workflow.testing.FunctionalTestCase):

    layer = zeit.workflow.testing.TMS_MOCK_LAYER

    def test_tms_wait_for_index_article(self):
        article = self.repository['testcontent']
        zope.interface.alsoProvides(
            article, zeit.content.article.interfaces.IArticle)
        data_factory = zope.component.getAdapter(
            article,
            zeit.workflow.interfaces.IPublisherData,
            name='tms')
        payload = data_factory.publish_json()
        assert payload == {'wait': True}

    def test_tms_only_waits_for_articles(self):
        content = self.repository['testcontent']
        data_factory = zope.component.getAdapter(
            content,
            zeit.workflow.interfaces.IPublisherData,
            name='tms')
        payload = data_factory.publish_json()
        assert payload == {'wait': False}

    def test_tms_ignores_content_without_tms_representation(self):
        content = self.repository['testcontent']
        self.layer.representation().return_value = None
        data_factory = zope.component.getAdapter(
            content,
            zeit.workflow.interfaces.IPublisherData,
            name='tms')
        payload = data_factory.publish_json()
        assert payload is None


class BigQueryPayloadTest(zeit.workflow.testing.FunctionalTestCase):

    layer = zeit.workflow.testing.TMS_MOCK_LAYER

    def setUp(self):
        super().setUp()
        FEATURE_TOGGLES.set('publish_bigquery_json')
        self.layer.representation().return_value = {
            'payload': {'document': {'uuid': '{urn:uuid:myuuid}'}}}
        with checked_out(self.repository['testcontent']):
            pass  # XXX trigger uuid generation
        self.article = self.repository['testcontent']
        zope.interface.alsoProvides(
            self.article, zeit.content.article.interfaces.IArticle)

    def test_includes_uniqueid_under_meta(self):
        data = zope.component.getAdapter(
            self.article, zeit.workflow.interfaces.IPublisherData,
            name='bigquery')
        for action in ['publish', 'retract']:
            d = getattr(data, f'{action}_json')()
            self.assertEqual(
                'http://xml.zeit.de/testcontent',
                d['properties']['meta']['url'])
            self.assertStartsWith(
                '{urn:uuid:', d['properties']['document']['uuid'])

    def test_moves_rtr_keywords_under_tagging(self):
        self.layer.representation().return_value = {
            'rtr_locations': [],
            'rtr_keywords': ['one', 'two'],
            'title': 'ignored',
        }
        data = zeit.workflow.testing.publish_json(self.article, 'bigquery')
        self.assertEqual({'rtr_locations': [], 'rtr_keywords': ['one', 'two']},
                         data['properties']['tagging'])


class BadgerfishTest(unittest.TestCase):

    def badgerfish(self, text):
        return zeit.workflow.publish_3rdparty.badgerfish(lxml.etree.XML(text))

    def test_text_becomes_dollar(self):
        self.assertEqual(
            {'a': {'$': 'b'}},
            self.badgerfish('<a>b</a>'))

    def test_children_become_nested_dict(self):
        self.assertEqual(
            {'a': {'b': {'$': 'c'},
                   'd': {'$': 'e'}}},
            self.badgerfish('<a><b>c</b><d>e</d></a>'))

    def test_children_same_name_become_list(self):
        self.assertEqual(
            {'a': {'b': [{'$': 'c'}, {'$': 'd'}]}},
            self.badgerfish('<a><b>c</b><b>d</b></a>'))

    def test_attributes_become_prefixed_with_at(self):
        self.assertEqual(
            {'a': {'$': 'b', '@c': 'd'}},
            self.badgerfish('<a c="d">b</a>'))

    def test_namespace_is_removed_from_tag(self):
        self.assertEqual(
            {'a': {}},
            self.badgerfish('<x:a xmlns:x="x" />'))

    def test_namespace_is_removed_from_attribute(self):
        self.assertEqual(
            {'a': {'@b': 'c'}},
            self.badgerfish('<a xmlns:x="x" x:b="c" />'))
