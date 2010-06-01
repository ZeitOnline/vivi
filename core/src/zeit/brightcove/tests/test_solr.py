# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.brightcove.solr
import zeit.brightcove.testing
import zeit.cms
import zeit.solr.interfaces
import zope.component
import zope.lifecycleevent


class TestSolrIndexing(zeit.brightcove.testing.BrightcoveTestCase):

    def setUp(self):
        super(TestSolrIndexing, self).setUp()
        self.solr = zope.component.getUtility(
            zeit.solr.interfaces.ISolr)
        self.public_solr = zope.component.getUtility(
            zeit.solr.interfaces.ISolr, name='public')
        # clear out indexing requests queued up by the test setup
        self.solr.reset_mock()
        self.public_solr.reset_mock()

    def test_updating_repository_should_index_contents(self):
        self.repository._data.clear()
        self.repository.update_from_brightcove()
        self.assertTrue(self.solr.update_raw.called)
        self.assertEquals(5, len(self.solr.update_raw.call_args_list))
        self.assertEquals(5, len(self.public_solr.update_raw.call_args_list))
        element_add = self.solr.update_raw.call_args_list[0][0][0]
        self.assertEquals(
            ['http://video.zeit.de/video/1234'],
            element_add.xpath("/add/doc/field[@name='uniqueId']"))
        self.assertEquals(
            ['http://flvurl'],
            element_add.xpath("/add/doc/field[@name='h264_url']"))
        element_add = self.solr.update_raw.call_args_list[1][0][0]
        self.assertEquals(
            ['http://video.zeit.de/video/9876'],
            element_add.xpath("/add/doc/field[@name='uniqueId']"))
        element_add = self.solr.update_raw.call_args_list[2][0][0]
        self.assertEquals(
            ['http://video.zeit.de/video/6789'],
            element_add.xpath("/add/doc/field[@name='uniqueId']"))
        element_add = self.solr.update_raw.call_args_list[3][0][0]
        self.assertEquals(
            ['http://video.zeit.de/playlist/2345'],
            element_add.xpath("/add/doc/field[@name='uniqueId']"))
        element_add = self.solr.update_raw.call_args_list[4][0][0]
        self.assertEquals(
            ['http://video.zeit.de/playlist/3456'],
            element_add.xpath("/add/doc/field[@name='uniqueId']"))

    def test_deleted_playlists_removed_from_solr(self):
        pls = self.repository['playlist:2345']
        pls.item_state = 'DELETED'
        zope.lifecycleevent.modified(pls)
        self.assertTrue(self.solr.delete.called)
        self.assertTrue(self.public_solr.delete.called)

    def test_active_videos_should_be_index(self):
        video = zeit.cms.interfaces.ICMSContent(
            "http://video.zeit.de/video/1234")
        video.item_state = 'ACTIVE'
        zope.lifecycleevent.modified(video)
        self.assertTrue(self.solr.update_raw.called)
        self.assertTrue(self.public_solr.update_raw.called)

    def test_inactive_videos_should_be_deleted_from_solr(self):
        video = zeit.cms.interfaces.ICMSContent(
            "http://video.zeit.de/video/1234")
        video.item_state = 'INACTIVE'
        zope.lifecycleevent.modified(video)
        self.assertTrue(self.solr.delete.called)
        self.assertTrue(self.public_solr.delete.called)

    def test_deleted_videos_should_be_deleted_from_solr(self):
        video = zeit.cms.interfaces.ICMSContent(
            "http://video.zeit.de/video/1234")
        video.item_state = 'DELETED'
        zope.lifecycleevent.modified(video)
        self.assertTrue(self.solr.delete.called)
        self.assertTrue(self.public_solr.delete.called)
