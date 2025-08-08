from unittest import mock

import zope.component
import zope.interface

import zeit.cms.repository.folder
import zeit.cms.testing
import zeit.push.testing


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer({}, bases=zeit.push.testing.CONFIG_LAYER)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(CONFIG_LAYER)
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER)
PUSH_LAYER = zeit.push.testing.UrbanairshipTemplateLayer(ZOPE_LAYER)


class PlayerMockLayer(zeit.cms.testing.Layer):
    def setUp(self):
        self['player'] = mock.Mock()
        zope.interface.alsoProvides(self['player'], zeit.content.video.interfaces.IPlayer)
        zope.component.getSiteManager().registerUtility(self['player'], name='brightcove')

    def tearDown(self):
        zope.component.getSiteManager().unregisterUtility(self['player'], name='brightcove')

    def testSetUp(self):
        self['player'].reset_mock()
        self['player'].get_video.return_value = {
            'renditions': (),
            'video_still': None,
        }


PLAYER_MOCK_LAYER = PlayerMockLayer()


LAYER = zeit.cms.testing.Layer((PUSH_LAYER, PLAYER_MOCK_LAYER))
WSGI_LAYER = zeit.cms.testing.WSGILayer(LAYER)


class TestCase(zeit.cms.testing.FunctionalTestCase):
    layer = LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER


def FunctionalDocFileSuite(*args, **kw):
    kw.setdefault('layer', WSGI_LAYER)
    return zeit.cms.testing.FunctionalDocFileSuite(*args, **kw)


def video_factory(self):
    from zeit.content.image.testing import create_image_group_with_master_image
    from zeit.content.video.video import Video

    with zeit.cms.testing.site(self.getRootFolder()):
        with zeit.cms.testing.interaction():
            video = Video()
            img = zeit.content.image.interfaces.IImages(video)
            img.image = create_image_group_with_master_image()
            yield video
            self.repository['video'] = video
    yield self.repository['video']
