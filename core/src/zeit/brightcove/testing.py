# coding: utf-8
from unittest import mock

import gocept.httpserverlayer.static
import transaction

import zeit.cms.testing
import zeit.content.video.testing


class MockAPILayer(zeit.cms.testing.Layer):
    def setUp(self):
        self.cmsapi_patch = mock.patch('zeit.brightcove.connection.CMSAPI._request')
        self.cmsapi_patch.start()
        self.playbackapi_patch = mock.patch('zeit.brightcove.connection.PlaybackAPI._request')
        self.playbackapi_patch.start()

    def tearDown(self):
        self.cmsapi_patch.stop()
        self.playbackapi_patch.stop()


MOCK_API_LAYER = MockAPILayer()
CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {
        'api-url': 'none',
        'oauth-url': 'none',
        'client-id': 'none',
        'client-secret': 'none',
        'client-email': 'vivi@example.com',
        'timeout': '300',
        'playback-url': 'none',
        'playback-policy-key': 'none',
        'playback-timeout': '3',
        'video-folder': 'video',
        'index-principal': 'zope.user',
    },
    patches={'zeit.cms': {'task-queue-brightcove': 'brightcove'}},
    bases=zeit.content.video.testing.CONFIG_LAYER,
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer((CONFIG_LAYER, MOCK_API_LAYER))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER)
WSGI_LAYER = zeit.cms.testing.WSGILayer(ZOPE_LAYER)
HTTP_STATIC_LAYER = gocept.httpserverlayer.static.Layer(name='HTTPStaticLayer', bases=(WSGI_LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER


class StaticBrowserTestCase(FunctionalTestCase):
    layer = HTTP_STATIC_LAYER


def update_repository(root):
    with zeit.cms.testing.site(root):
        with transaction.manager:
            zeit.brightcove.update.update_from_brightcove()
