from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.interfaces import ICMSContent
from zeit.cms.workflow.interfaces import IPublishInfo, IPublish
from zeit.content.image.testing import create_image_group_with_master_image
import pytest
import requests_mock
import sys
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
import zeit.workflow.testing
import zope.app.appsetup.product
import zope.component
import zope.i18n


class Publisher3rdPartyTest(zeit.workflow.testing.FunctionalTestCase):

    layer = zeit.content.article.testing.LAYER

    @pytest.fixture(autouse=True)
    def caplog(self, caplog):
        self.caplog = caplog

    def test_authordashboard_is_notified(self):
        FEATURE_TOGGLES.set('new_publisher')
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
        FEATURE_TOGGLES.set('new_publisher')
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
                {'path': '/online/2007/01/Somalia'},
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
        FEATURE_TOGGLES.set('new_publisher')
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).urgent = True
        self.assertFalse(IPublishInfo(article).published)
        with requests_mock.Mocker() as rmock:
            response = rmock.post(
                'http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            result_comments = result['comments']
            result_comments.pop('uuid')  # NOTE changes each run
            self.assertEqual({
                'comments_allowed': False,
                'pre_moderated': False,
                'type': 'commentsection',
                'unique_id': 'http://xml.zeit.de/online/2007/01/Somalia',
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
        FEATURE_TOGGLES.set('new_publisher')
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
                {'path': '/online/2007/01/Somalia'},
                result_fbnt)
        self.assertTrue(IPublishInfo(article).published)

    def test_facebooknewstab_skipped_date_first_released(self):
        FEATURE_TOGGLES.set('new_publisher')
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
        FEATURE_TOGGLES.set('new_publisher')
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
        FEATURE_TOGGLES.set('new_publisher')
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
        FEATURE_TOGGLES.set('new_publisher')
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
                [
                    'authors', 'body', 'hasAudio', 'headline', 'publishDate',
                    'section', 'series', 'subtitle', 'supertitle', 'tags',
                    'teaser', 'url', 'uuid'],
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
        # disable the max-age filter
        config['speechbert-max-age'] = sys.maxsize
        config['speechbert-ignore-genres'] = 'rezept-vorstellung'
        data_factory = zope.component.getAdapter(
            article,
            zeit.workflow.interfaces.IPublisherData,
            name="speechbert")
        assert data_factory.publish_json() is None
        config['speechbert-ignore-genres'] = ''
        data_factory = zope.component.getAdapter(
            article,
            zeit.workflow.interfaces.IPublisherData,
            name="speechbert")
        assert data_factory.publish_json() is not None

    def test_speechbert_ignore_templates(self):
        article = ICMSContent(
            'http://xml.zeit.de/zeit-magazin/wochenmarkt/rezept')
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        # disable the max-age filter
        config['speechbert-max-age'] = sys.maxsize
        config['speechbert-ignore-templates'] = 'article'
        data_factory = zope.component.getAdapter(
            article,
            zeit.workflow.interfaces.IPublisherData,
            name="speechbert")
        assert data_factory.publish_json() is None
        config['speechbert-ignore-templates'] = ''
        data_factory = zope.component.getAdapter(
            article,
            zeit.workflow.interfaces.IPublisherData,
            name="speechbert")
        assert data_factory.publish_json() is not None

    def test_speechbert_max_age(self):
        article = ICMSContent(
            'http://xml.zeit.de/zeit-magazin/wochenmarkt/rezept')
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        data_factory = zope.component.getAdapter(
            article,
            zeit.workflow.interfaces.IPublisherData,
            name="speechbert")
        assert data_factory.publish_json() is None
        config['speechbert-max-age'] = sys.maxsize
        data_factory = zope.component.getAdapter(
            article,
            zeit.workflow.interfaces.IPublisherData,
            name="speechbert")
        assert data_factory.publish_json() is not None


class SpeechbertPayloadTest(zeit.workflow.testing.FunctionalTestCase):

    layer = zeit.content.article.testing.LAYER

    def create_author(self, firstname, lastname, key):
        author = zeit.content.author.author.Author()
        author.firstname = firstname
        author.lastname = lastname
        self.repository[key] = author

    @pytest.fixture(autouse=True)
    def monkeypatch(self, monkeypatch):
        monkeypatch.setattr(
            zeit.workflow.publish_3rdparty.Speechbert,
            'ignore',
            lambda s, d, m: False)

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
        data_factory = zope.component.getAdapter(
            article,
            zeit.workflow.interfaces.IPublisherData,
            name="speechbert")
        payload = data_factory.publish_json()
        del payload['body']  # not relevant in this test
        assert payload == dict(
            access='abo',
            authors=['Eva Biringer'],
            channels='zeit-magazin essen-trinken',
            genre='rezept-vorstellung',
            hasAudio='true',
            headline='Vier Rezepte für eine Herdplatte',
            image='http://localhost/img-live-prefix/group/wide__820x461',
            lastModified='2020-04-14T09:19:59.618155+00:00',
            publishDate='2020-04-14T09:19:59.618155+00:00',
            section='zeit-magazin',
            subsection='essen-trinken',
            subtitle=(
                'Ist genug Brot und Kuchen gebacken, bleibt endlich wieder '
                'Zeit, zu kochen. Mit diesen One-Pot-Gerichten können Sie den '
                'Zuckerschock vom Osterwochenende kontern.'),
            tags=['Testtag', 'Testtag2', 'Testtag3'],
            teaser=(
                'Ist genug Brot und Kuchen gebacken, '
                'bleibt endlich wieder Zeit, zu kochen.'),
            url='',
            uuid='16e82986-cdc0-492d-84e8-267d09b4ab53')

    def test_speechbert_payload_access_free(self):
        article = ICMSContent(
            'http://xml.zeit.de/online/2007/01/weissrussland-russland-gas')
        data_factory = zope.component.getAdapter(
            article,
            zeit.workflow.interfaces.IPublisherData,
            name="speechbert")
        payload = data_factory.publish_json()
        assert article.access == 'free'
        assert 'access' not in payload

    def test_speechbert_payload_no_authors(self):
        article = ICMSContent(
            'http://xml.zeit.de/online/2007/01/terror-abschuss-schaeuble')
        data_factory = zope.component.getAdapter(
            article,
            zeit.workflow.interfaces.IPublisherData,
            name="speechbert")
        payload = data_factory.publish_json()
        assert article.authors == ()
        assert payload['authors'] == []

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
        data_factory = zope.component.getAdapter(
            article,
            zeit.workflow.interfaces.IPublisherData,
            name="speechbert")
        payload = data_factory.publish_json()
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
        data_factory = zope.component.getAdapter(
            article,
            zeit.workflow.interfaces.IPublisherData,
            name="speechbert")
        payload = data_factory.publish_json()
        assert article.channels == ()
        assert 'channels' not in payload

    def test_speechbert_payload_single_channel(self):
        article = ICMSContent(
            'http://xml.zeit.de/online/2022/08/trockenheit')
        data_factory = zope.component.getAdapter(
            article,
            zeit.workflow.interfaces.IPublisherData,
            name="speechbert")
        payload = data_factory.publish_json()
        assert article.channels == (('News', None),)
        assert payload['channels'] == 'News'

    def test_speechbert_payload_series(self):
        article = ICMSContent(
            'http://xml.zeit.de/online/2007/01/weissrussland-russland-gas')
        data_factory = zope.component.getAdapter(
            article,
            zeit.workflow.interfaces.IPublisherData,
            name="speechbert")
        payload = data_factory.publish_json()
        assert article.serie is not None
        assert payload['series'] == '-'

    def test_speechbert_payload_supertitle(self):
        article = ICMSContent(
            'http://xml.zeit.de/online/2007/01/weissrussland-russland-gas')
        data_factory = zope.component.getAdapter(
            article,
            zeit.workflow.interfaces.IPublisherData,
            name="speechbert")
        payload = data_factory.publish_json()
        assert article.supertitle == 'Geopolitik'
        assert payload['supertitle'] == 'Geopolitik'
