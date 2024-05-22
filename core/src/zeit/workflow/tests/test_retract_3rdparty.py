import requests_mock
import zope.component

from zeit.cms.interfaces import ICMSContent
from zeit.cms.workflow.interfaces import IPublish, IPublisher, IPublishInfo
import zeit.workflow.publisher
import zeit.workflow.testing


class Retract3rdPartyTest(zeit.workflow.testing.FunctionalTestCase):
    layer = zeit.workflow.testing.ARTICLE_LAYER

    def setUp(self):
        super().setUp()
        self.gsm = zope.component.getGlobalSiteManager()
        self.gsm.registerUtility(zeit.workflow.publisher.Publisher(), IPublisher)

    def test_ignore_3rdparty_list_is_respected(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        self.assertFalse(IPublishInfo(article).published)
        with requests_mock.Mocker() as rmock:
            zeit.workflow.publish_3rdparty.PublisherData.ignore = ['speechbert']
            response = rmock.post('http://localhost:8060/test/retract', status_code=200)
            IPublish(article).retract(background=True)
            (result,) = response.last_request.json()
            assert 'speechbert' not in result
            assert 'bigquery' in result
        zeit.workflow.publish_3rdparty.PublisherData.ignore = []  # reset
        self.assertFalse(IPublishInfo(article).published)

    def test_authordashboard_is_ignored_during_retraction(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).published = True
        self.assertTrue(IPublishInfo(article).published)
        with requests_mock.Mocker() as rmock:
            response = rmock.post('http://localhost:8060/test/retract', status_code=200)
            IPublish(article).retract(background=False)
            (result,) = response.last_request.json()
            assert 'authordashboard' not in result
        self.assertFalse(IPublishInfo(article).published)

    def test_bigquery_is_retracted(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).published = True
        self.assertTrue(IPublishInfo(article).published)
        with requests_mock.Mocker() as rmock:
            response = rmock.post('http://localhost:8060/test/retract', status_code=200)
            IPublish(article).retract(background=False)
            (result,) = response.last_request.json()
            result_bq = result['bigquery']
            self.assertEqual(
                'http://localhost/live-prefix/online/2007/01/Somalia',
                result_bq['properties']['meta']['url'],
            )
        self.assertFalse(IPublishInfo(article).published)

    def test_comments_are_ignored_during_retraction(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).published = True
        self.assertTrue(IPublishInfo(article).published)
        with requests_mock.Mocker() as rmock:
            response = rmock.post('http://localhost:8060/test/retract', status_code=200)
            IPublish(article).retract(background=False)
            (result,) = response.last_request.json()
            assert 'comments' not in result
        self.assertFalse(IPublishInfo(article).published)

    def test_speechbert_is_retracted(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).published = True
        self.assertTrue(IPublishInfo(article).published)
        with requests_mock.Mocker() as rmock:
            response = rmock.post('http://localhost:8060/test/retract', status_code=200)
            IPublish(article).retract(background=False)
            (result,) = response.last_request.json()
            assert 'speechbert' in result
        self.assertFalse(IPublishInfo(article).published)

    def test_speechbert_ignore_genres(self):
        article = ICMSContent('http://xml.zeit.de/zeit-magazin/wochenmarkt/rezept')
        config = zope.app.appsetup.product.getProductConfiguration('zeit.workflow')
        config['speechbert-ignore-genres'] = 'rezept-vorstellung'
        data_factory = zope.component.getAdapter(
            article, zeit.workflow.interfaces.IPublisherData, name='speechbert'
        )
        # for retraction this is NOT ignored
        assert data_factory.retract_json() is not None

    def test_speechbert_ignore_templates(self):
        article = ICMSContent('http://xml.zeit.de/zeit-magazin/wochenmarkt/rezept')
        config = zope.app.appsetup.product.getProductConfiguration('zeit.workflow')
        config['speechbert-ignore-templates'] = 'article'
        data_factory = zope.component.getAdapter(
            article, zeit.workflow.interfaces.IPublisherData, name='speechbert'
        )
        # for retraction this is NOT ignored
        assert data_factory.retract_json() is not None

    def test_tms_retract_article(self):
        article = self.repository['testcontent']
        data_factory = zope.component.getAdapter(
            article, zeit.workflow.interfaces.IPublisherData, name='tms'
        )
        payload = data_factory.retract_json()
        assert payload == {}

    def test_tms_retract_ignores_content_without_tms_representation(self):
        content = self.repository['testcontent']
        zeit.workflow.testing.MockTMSRepresentation.result = None
        data_factory = zope.component.getAdapter(
            content, zeit.workflow.interfaces.IPublisherData, name='tms'
        )
        payload = data_factory.retract_json()
        assert payload is None
