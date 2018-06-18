# coding: utf-8
from __future__ import absolute_import
import mock
import plone.testing
import transaction
import zeit.cms.testing
import zeit.content.video.testing
import zeit.solr.testing
import zeit.workflow.testing


product_config = """\
<product-config zeit.brightcove>
    api-url none
    oauth-url none
    client-id none
    client-secret none
    timeout 300

    playback-url none
    playback-policy-key none
    playback-timeout 3

    video-folder video
    playlist-folder video/playlist
    index-principal zope.user
</product-config>
"""

# XXX appending to product config is not very well supported right now
cms_product_config = zeit.cms.testing.cms_product_config.replace(
    '</product-config>', """\
  task-queue-brightcove brightcove
</product-config>""")

ZCML_LAYER = zeit.cms.testing.ZCMLLayer('ftesting.zcml', product_config=(
    cms_product_config +
    zeit.solr.testing.product_config +
    zeit.workflow.testing.product_config +
    product_config))


def update_repository(root):
    with zeit.cms.testing.site(root):
        with transaction.manager:
            zeit.brightcove.update.update_from_brightcove()


class BrightcoveLayer(plone.testing.Layer):

    defaultBases = (ZCML_LAYER, zeit.solr.testing.SOLR_MOCK_LAYER)

    def setUp(self):
        self.cmsapi_patch = mock.patch(
            'zeit.brightcove.connection.CMSAPI._request')
        self.cmsapi_patch.start()
        self.playbackapi_patch = mock.patch(
            'zeit.brightcove.connection.PlaybackAPI._request')
        self.playbackapi_patch.start()

    def tearDown(self):
        self.cmsapi_patch.stop()
        self.playbackapi_patch.stop()

LAYER = BrightcoveLayer()
