from unittest import mock

from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.content.image.testing import create_image_group
from zeit.cms.interfaces import ICMSContent
from zeit.cms.workflow.interfaces import IPublishInfo, IPublish
import requests_mock
import zeit.content.article.testing
import zeit.workflow.testing
import zope.component


class Retract3rdPartyTest(zeit.workflow.testing.FunctionalTestCase):
    layer = zeit.content.article.testing.LAYER

    def setUp(self):
        self.patch = mock.patch('zeit.retresco.interfaces.ITMSRepresentation')
        self.representation = self.patch.start()
        super().setUp()

    def tearDown(self):
        self.patch.stop()
        super().tearDown()

    def test_authordashboard_is_ignored_during_retraction(self):
        FEATURE_TOGGLES.set('new_publisher')
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).urgent = True
        IPublishInfo(article).published = True
        self.assertTrue(IPublishInfo(article).published)
        with requests_mock.Mocker() as rmock:
            response = rmock.post(
                'http://localhost:8060/test/retract', status_code=200)
            IPublish(article).retract(background=False)
            (result,) = response.last_request.json()
            assert 'authordashboard' not in result
        self.assertFalse(IPublishInfo(article).published)

    def test_bigquery_is_retracted(self):
        FEATURE_TOGGLES.set('new_publisher')
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).urgent = True
        IPublishInfo(article).published = True
        self.assertTrue(IPublishInfo(article).published)
        with requests_mock.Mocker() as rmock:
            response = rmock.post(
                'http://localhost:8060/test/retract', status_code=200)
            IPublish(article).retract(background=False)
            (result,) = response.last_request.json()
            result_bq = result['bigquery']
            self.assertEqual(
                {'path': '/online/2007/01/Somalia'},
                result_bq)
        self.assertFalse(IPublishInfo(article).published)

    def test_comments_are_ignored_during_retraction(self):
        FEATURE_TOGGLES.set('new_publisher')
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).urgent = True
        IPublishInfo(article).published = True
        self.assertTrue(IPublishInfo(article).published)
        with requests_mock.Mocker() as rmock:
            response = rmock.post(
                'http://localhost:8060/test/retract', status_code=200)
            IPublish(article).retract(background=False)
            (result,) = response.last_request.json()
            assert 'comments' not in result
        self.assertFalse(IPublishInfo(article).published)

    def test_facebooknewstab_is_retracted(self):
        FEATURE_TOGGLES.set('new_publisher')
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).urgent = True
        IPublishInfo(article).published = True
        self.assertTrue(IPublishInfo(article).published)
        with requests_mock.Mocker() as rmock:
            response = rmock.post(
                'http://localhost:8060/test/retract', status_code=200)
            IPublish(article).retract(background=False)
            (result,) = response.last_request.json()
            result_fbnt = result['facebooknewstab']
            self.assertEqual(
                {'path': '/online/2007/01/Somalia'},
                result_fbnt)
        self.assertFalse(IPublishInfo(article).published)

    def test_speechbert_is_retracted(self):
        FEATURE_TOGGLES.set('new_publisher')
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).urgent = True
        IPublishInfo(article).published = True
        self.assertTrue(IPublishInfo(article).published)
        with requests_mock.Mocker() as rmock:
            response = rmock.post(
                'http://localhost:8060/test/retract', status_code=200)
            IPublish(article).retract(background=False)
            (result,) = response.last_request.json()
            result_sb = result['speechbert']
            self.assertEqual(['uuid'], sorted(result_sb.keys()))
        self.assertFalse(IPublishInfo(article).published)

    def test_speechbert_ignore_genres(self):
        article = ICMSContent(
            'http://xml.zeit.de/zeit-magazin/wochenmarkt/rezept')
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        config['speechbert-ignore-genres'] = 'rezept-vorstellung'
        data_factory = zope.component.getAdapter(
            article,
            zeit.workflow.interfaces.IPublisherData,
            name="speechbert")
        # for retraction this is NOT ignored
        assert data_factory.retract_json() is not None

    def test_speechbert_ignore_templates(self):
        article = ICMSContent(
            'http://xml.zeit.de/zeit-magazin/wochenmarkt/rezept')
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        config['speechbert-ignore-templates'] = 'article'
        data_factory = zope.component.getAdapter(
            article,
            zeit.workflow.interfaces.IPublisherData,
            name="speechbert")
        # for retraction this is NOT ignored
        assert data_factory.retract_json() is not None

    def test_tms_retract_article(self):
        article = ICMSContent(
            'http://xml.zeit.de/online/2007/01/Somalia')
        with checked_out(article):
            pass  # trigger uuid creation
        data_factory = zope.component.getAdapter(
            article,
            zeit.workflow.interfaces.IPublisherData,
            name='tms')
        payload = data_factory.retract_json()
        assert payload == {}

    def test_tms_retract_news_image_group_is_ignored(self):
        import zeit.cms.repository.folder
        image_group = create_image_group()
        with checked_out(image_group):
            pass  # trigger uuid creation
        self.representation().return_value = None
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        repository['news'] = zeit.cms.repository.folder.Folder()
        repository['news']['group'] = image_group

        image_group = ICMSContent('http://xml.zeit.de/news/group/')
        data_factory = zope.component.getAdapter(
            image_group,
            zeit.workflow.interfaces.IPublisherData,
            name='tms')
        payload = data_factory.retract_json()
        assert payload is None
