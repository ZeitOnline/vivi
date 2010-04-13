# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import pkg_resources
import zeit.brightcove.solr
import zeit.brightcove.testing
import zeit.cms
import zeit.solr.interfaces
import zope.component


class TestSolrIndexing(zeit.brightcove.testing.BrightcoveTestCase):

    def setUp(self):
        super(TestSolrIndexing, self).setUp()
        self.solr = zope.component.getUtility(
            zeit.solr.interfaces.ISolr)
        self.public_solr = zope.component.getUtility(
            zeit.solr.interfaces.ISolr, name='public')

    def tearDown(self):
        zope.component.getSiteManager().unregisterUtility(self.public_solr, name='public')
        super(TestSolrIndexing, self).tearDown()

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

    def test_solr_active(self):
        video = zeit.cms.interfaces.ICMSContent("http://video.zeit.de/video/1234")
        video.item_state = 'ACTIVE'
        zeit.brightcove.solr._update_single_content(video)
        self.assertTrue(self.solr.update_raw.called)
        self.assertTrue(self.public_solr.update_raw.called)

    def test_solr_inactive(self):
        video = zeit.cms.interfaces.ICMSContent("http://video.zeit.de/video/1234")
        video.item_state = 'INACTIVE'
        zeit.brightcove.solr._update_single_content(video)
        self.assertTrue(self.solr.delete.called)
        self.assertTrue(self.public_solr.delete.called)

    def test_solr_deleted(self):
        video = zeit.cms.interfaces.ICMSContent("http://video.zeit.de/video/1234")
        video.item_state = 'DELETED'
        zeit.brightcove.solr._update_single_content(video)
        self.assertTrue(self.solr.delete.called)
        self.assertTrue(self.public_solr.delete.called)

    def test_empty_playlists(self):
        zeit.brightcove.solr._empty_playlists()
        self.assertTrue(self.solr.delete)
        self.assertTrue(self.public_solr.delete)
