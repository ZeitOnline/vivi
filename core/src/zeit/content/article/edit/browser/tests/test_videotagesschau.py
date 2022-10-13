# coding: utf-8
import zeit.content.article.edit.browser.testing
import zeit.content.article.edit.interfaces
import zeit.content.article.edit.videotagesschau
import zope.component
import json
import plone.testing

HTTP_LAYER = zeit.cms.testing.HTTPLayer(
    zeit.cms.testing.RecordingRequestHandler,
    name='HTTPLayer', module=__name__)

LAYER = plone.testing.Layer(
    bases=(HTTP_LAYER, zeit.content.article.testing.ZOPE_LAYER),
    name='HDokLayer', module=__name__)

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
                      "published_start_time": "2022-09-32T33:02:00",
                      "score": 303.98643,
                      "search_strategy": "hotnews-no-local",
                      "short_synopsis": "Das ist Video 3",
                      "start_of_availability": "2022-09-32T33:02:59",
                      "thumbnail_uris": {"fullhd": "tages.schau/thumb3",
                                         "large": "tages.schau/thumb2",
                                         "small": "tages.schau/thumb3"},
                      "video_uris": {"hd": "tages.schau/video3_hd",
                                     "hlsStream": "tages.schau/video3_hls",
                                     "hq": "tages.schau/video3_hq",
                                     "ln": "tages.schau/video3_ln"}}
                    ],
 "src_txt_hash": "881424269bcdd572e37c6ef3ff702baefb7845e9a12a22518e062e0b5f194e9a"}
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
        self.assertTrue('<strong>Video 2</strong> (hotnews-no-local)<br />'
            '<a href="tages.schau/video2_hd" target="_blank">open video</a>'
            '</label>' in brwsr.contents)
