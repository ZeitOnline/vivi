# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.brightcove.testing
import pkg_resources
import zeit.brightcove.solr
import zeit.solr.testing


class BrightcoveSolrLayer(zeit.brightcove.testing.BrightcoveLayer):

    config_file = pkg_resources.resource_filename(
        __name__, 'ftesting-solr.zcml')
    module = __name__
    __name__ =  'BrightcoveSolrLayer'
    product_config=(
        zeit.brightcove.testing.product_config +
        zeit.solr.testing.product_config)


class TestSolrIndexing(zeit.solr.testing.MockedFunctionalTestCase):

    layer = BrightcoveSolrLayer()

    def test_indexing_changed_videos(self):
        zeit.brightcove.solr._index_changed_videos_and_playlists()
        self.assertTrue(self.solr.update_raw.called)
        self.assertEquals(4, len(self.solr.update_raw.call_args_list))
        element_add = self.solr.update_raw.call_args_list[0][0][0]
        self.assertEquals(
            ['http://video.zeit.de/video/1234'],
            element_add.xpath("/add/doc/field[@name='uniqueId']"))
        element_add = self.solr.update_raw.call_args_list[1][0][0]
        self.assertEquals(
            ['http://video.zeit.de/video/9876'],
            element_add.xpath("/add/doc/field[@name='uniqueId']"))
        element_add = self.solr.update_raw.call_args_list[2][0][0]
        self.assertEquals(
            ['http://video.zeit.de/playlist/2345'],
            element_add.xpath("/add/doc/field[@name='uniqueId']"))
        element_add = self.solr.update_raw.call_args_list[3][0][0]
        self.assertEquals(
            ['http://video.zeit.de/playlist/3456'],
            element_add.xpath("/add/doc/field[@name='uniqueId']"))
