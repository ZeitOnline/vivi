from zeit.brightcove.convert2 import Video as BCVideo
from zeit.content.video.video import Video as CMSVideo
import zeit.brightcove.testing
import zeit.cms.testing


class VideoTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.brightcove.testing.ZCML_LAYER

    def test_converts_cms_fields_to_bc_names(self):
        cms = CMSVideo()
        cms.title = u'title'
        cms.teaserText = u'teaser'
        bc = BCVideo.from_cms(cms)
        self.assertEqual('title', bc.title)
        self.assertEqual('title', bc.data['name'])
        self.assertEqual('teaser', bc.teaserText)
        self.assertEqual('teaser', bc.data['description'])

    def test_setting_readonly_field_raises(self):
        bc = BCVideo()
        with self.assertRaises(AttributeError):
            bc.id = 'id'
