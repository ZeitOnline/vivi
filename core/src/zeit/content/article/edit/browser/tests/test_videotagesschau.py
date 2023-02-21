# coding: utf-8
import json
import zope.component
from unittest import mock
import lxml.objectify
from zeit.cms.content.sources import FEATURE_TOGGLES
import zeit.content.article.edit.browser.testing
import zeit.content.article.edit.interfaces
import zeit.content.article.edit.videotagesschau

MOCKDEFAULTBROKEN = '''
{"cutoff": 1.975
}
'''

MOCKDEFAULTEMPTY = '''
{"cutoff": 1.975,
 "recommendations": [],
 "src_txt_hash": "881424269bcdd572e37c6ef3ff702baefb7845e9a12a22518e062e09a"
}
'''

MOCKDEFAULT = '''
{"cutoff": 1.975,
 "recommendations": [{"main_title": "Video 1",
                      "program_id": "crid://daserste.de/crid1",
                      "published_start_time": "2022-09-12T11:02:00",
                      "score": 101.98643,
                      "search_strategy": "hotnews-no-local",
                      "short_synopsis": "Das ist Video 1",
                      "start_of_availability": "2022-09-12T11:02:59",
                      "thumbnail_uris": {"fullhd": "tages.schau/thumb1",
                                         "large": "tages.schau/thumb2",
                                         "small": "tages.schau/thumb3"},
                      "video_uris": {"hd": "tages.schau/video1_hd",
                                     "hlsStream": "tages.schau/video1_hls",
                                     "hq": "tages.schau/video1_hq",
                                     "ln": "tages.schau/video1_ln"}},
                     {"main_title": "Video 2",
                      "program_id": "crid://daserste.de/crid2",
                      "published_start_time": "2022-09-22T22:02:00",
                      "score": 202.98643,
                      "search_strategy": "hotnews-no-local",
                      "short_synopsis": "Das ist Video 2",
                      "start_of_availability": "2022-09-22T22:02:59",
                      "thumbnail_uris": {"fullhd": "tages.schau/thumb2",
                                         "large": "tages.schau/thumb2",
                                         "small": "tages.schau/thumb3"},
                      "video_uris": {"hd": "tages.schau/video2_hd",
                                     "hlsStream": "tages.schau/video2_hls",
                                     "hq": "tages.schau/video2_hq",
                                     "ln": "tages.schau/video2_ln"}},
                     {"main_title": "Video 3",
                      "program_id": "crid://daserste.de/crid3",
                      "published_start_time": "2022-09-23T23:02:00",
                      "score": 303.98643,
                      "search_strategy": "hotnews-no-local",
                      "short_synopsis": "Das ist Video 3",
                      "start_of_availability": "2022-09-23T23:02:59",
                      "thumbnail_uris": {"fullhd": "tages.schau/thumb3",
                                         "large": "tages.schau/thumb2",
                                         "small": "tages.schau/thumb3"},
                      "video_uris": {"hd": "tages.schau/video3_hd",
                                     "hlsStream": "tages.schau/video3_hls",
                                     "hq": "tages.schau/video3_hq",
                                     "ln": "tages.schau/video3_ln"}}
                    ],
 "src_txt_hash": "881424269bcdd572e37c6ef3ff702baefb7845e9a12a22518e062e09a"}
'''


class Form(zeit.content.article.edit.browser.testing.BrowserTestCase):

    block_type = 'videotagesschau'

    def test_api_call_result_renders_correct_select_form(self):
        api = zope.component.getUtility(
            zeit.content.article.edit.interfaces.IVideoTagesschauAPI)
        api.request_videos.return_value = json.loads(MOCKDEFAULT)
        article = self.get_article(with_empty_block=True)
        brwsr = self.browser
        brwsr.open(
            'editable-body/blockname/@@edit-videotagesschau?show_form=1')
        self.assertEqual(len(brwsr.xpath('//input[@type="radio"]')), 1)
        brwsr.getControl('generate-video-recommendation').click()
        brwsr.open('@@edit-videotagesschau?show_form=1')
        api.request_videos.assert_called_with(article)
        self.assertEqual(len(brwsr.xpath('//input[@type="radio"]')), 4)
        self.assertEqual(
            'radio', brwsr.getControl('Video 1')._elem.get('type'))
        self.assertEqual(
            'crid://daserste.de/crid1', brwsr.getControl('Video 1').value)
        self.assertEqual(
            'crid://daserste.de/crid3', brwsr.getControl('Video 3').value)
        self.assertTrue(
            '<strong>Video 2</strong> - 2022-09-22 22:02:00 '
            '(hotnews-no-local)<br />'
            '<a href="tages.schau/video2_hd" target="_blank">open video</a>'
            '</label>' in brwsr.contents)

    def test_api_call_empty_recommendations_triggers_errormessage(self):
        api = zope.component.getUtility(
            zeit.content.article.edit.interfaces.IVideoTagesschauAPI)
        api.request_videos.return_value = json.loads(MOCKDEFAULTEMPTY)
        self.get_article(with_empty_block=True)
        brwsr = self.browser
        brwsr.open(
            'editable-body/blockname/@@edit-videotagesschau?show_form=1')
        self.assertEqual(len(brwsr.xpath('//input[@type="radio"]')), 1)
        brwsr.getControl('generate-video-recommendation').click()
        self.assertEqual(len(brwsr.xpath('//ul[@class="errors"]')), 1)
        self.assertEllipsis('...No tagesschau video recommendation found...', brwsr.contents)

    def test_api_call_fails_triggers_errormessage(self):
        api = zope.component.getUtility(
            zeit.content.article.edit.interfaces.IVideoTagesschauAPI)
        api.request_videos.return_value = json.loads(MOCKDEFAULTBROKEN)
        self.get_article(with_empty_block=True)
        brwsr = self.browser
        brwsr.open(
            'editable-body/blockname/@@edit-videotagesschau?show_form=1')
        self.assertEqual(len(brwsr.xpath('//input[@type="radio"]')), 1)
        brwsr.getControl('generate-video-recommendation').click()
        self.assertEqual(len(brwsr.xpath('//ul[@class="errors"]')), 1)
        self.assertEllipsis('...Error while requesting tagesschau API...', brwsr.contents)


class Form2(zeit.content.article.testing.FunctionalTestCase):

    def test_correct_payload_is_extracted_from_article_attributes(self):
        article = self.get_article()
        article.uniqueId = 'http://xml.zeit.de/content/fuer/die/taggesschau'
        body = ("<division><p>Das ist Tagesschau relevant.</p>"
                "<portraitbox>uninteressant</portraitbox></division>"
                "<division><p>Auch das ist Tagesschau relevant.</p>"
                "</division>")
        article.xml.body = lxml.objectify.XML(
            '<body>%s</body>' % body)
        article.title = 'Tagesschaurelevanter Artikel'
        zeit.cms.content.interfaces.IUUID(article).id = 'myid'
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.content.article')
        api = zeit.content.article.edit.videotagesschau.VideoTagesschauAPI(
            config)
        payload = api._prepare_payload(article)
        self.assertEqual('myid', payload['article_custom_id'])
        self.assertEqual(
            'Tagesschaurelevanter Artikel',
            payload['article_title'])
        self.assertEqual(
            'Das ist Tagesschau relevant. Auch das ist '
            'Tagesschau relevant.', payload['article_text'])
        self.assertEqual(
            '/content/fuer/die/taggesschau',
            payload['article_uri'])

        article.uniqueId = 'http://xml.zeit.de/artikel/pfad/111-aaa.tmp'
        payload = api._prepare_payload(article)
        self.assertEqual(
            '/artikel/pfad/tagesschaurelevanter-artikel',
            payload['article_uri'])

    def test_api_request_calls(self):
        article = self.get_article()
        article.uniqueId = 'http://xml.zeit.de/content/fuer/die/taggesschau'
        body = ("<division><p>Das ist Tagesschau relevant.</p>"
                "<portraitbox>uninteressant</portraitbox></division>"
                "<division><p>Auch das ist Tagesschau relevant.</p>"
                "</division>")
        article.xml.body = lxml.objectify.XML(
            '<body>%s</body>' % body)
        article.title = 'Tagesschaurelevanter Artikel'
        zeit.cms.content.interfaces.IUUID(article).id = 'myid'
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.content.article')
        api = zeit.content.article.edit.videotagesschau.VideoTagesschauAPI(
            config)
        FEATURE_TOGGLES.unset('ard_sync_api')
        with mock.patch('zeit.content.article.edit.'
                        'videotagesschau.VideoTagesschauAPI._request') as rq:
            api_request = api.request_videos(article)
            path, args = rq.call_args_list[0]
            self.assertEqual('GET https://ard-tagesschau/get/'
                             '6b0a8d0a2d3724730be6bde771c6c4cdd183757367'
                             '9289abd8809a881e34cd4f', path[0])
            path, args = rq.call_args_list[1]
            self.assertEqual('POST https://ard-tagesschau/post?SIG_URI=XYZ'
                             '&API_KEY=1a2b3c4d5e&ART_HASH=6b0a8d0a2d37247'
                             '30be6bde771c6c4cdd1837573679289abd8809a881e3'
                             '4cd4f', path[0])
            path, args = rq.call_args_list[2]
            self.assertEqual('GET https://ard-tagesschau/get/'
                             '6b0a8d0a2d3724730be6bde771c6c4cdd183757367'
                             '9289abd8809a881e34cd4f', path[0])
            assert isinstance(api_request, dict)
            assert isinstance(api_request['recommendations'], list)
        FEATURE_TOGGLES.set('ard_sync_api')
        with mock.patch('zeit.content.article.edit.'
                        'videotagesschau.VideoTagesschauAPI._request') as rq:
            api_request = api.request_videos(article)
            path, args = rq.call_args_list[1]
            self.assertEqual('POST https://ard-tagesschau/post/sync'
                             '?SIG_URI=XYZ'
                             '&API_KEY=1a2b3c4d5e&ART_HASH=6b0a8d0a2d37247'
                             '30be6bde771c6c4cdd1837573679289abd8809a881e3'
                             '4cd4f', path[0])
            assert isinstance(api_request, dict)
            assert isinstance(api_request['recommendations'], list)
