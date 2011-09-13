# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest2 as unittest  # XXX
import zeit.brightcove.solr
import zeit.brightcove.testing
import zeit.cms
import zeit.solr.interfaces
import zope.component
import zope.lifecycleevent


@unittest.skip('not yet')
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

    def test_interface(self):
        import zope.interface.verify
        updater = zeit.brightcove.solr.Updater(mock.sentinel.video)
        zope.interface.verify.verifyObject(
            zeit.solr.interfaces.IUpdater, updater)

    def test_updating_repository_should_index_contents(self):
        for key in self.repository._data:
            del self.repository._data[key]
        self.repository.update_from_brightcove()
        self.assertTrue(self.solr.update_raw.called)
        self.assertEquals(5, len(self.solr.update_raw.call_args_list))
        self.assertEquals(5, len(self.public_solr.update_raw.call_args_list))
        element_add = self.solr.update_raw.call_args_list[0][0][0]
        self.assertEquals(
            ['http://xml.zeit.de/video/2010-03/1234'],
            element_add.xpath("/add/doc/field[@name='uniqueId']"))
        self.assertEquals(
            ['http://flvurl'],
            element_add.xpath("/add/doc/field[@name='h264_url']"))
        self.assertEquals(
            [True],
            element_add.xpath("/add/doc/field[@name='banner']"))
        self.assertEquals(
            [99887],
            element_add.xpath("/add/doc/field[@name='banner-id']"))

        element_add = self.solr.update_raw.call_args_list[1][0][0]
        self.assertEquals(
            ['http://xml.zeit.de/video/2010-03/9876'],
            element_add.xpath("/add/doc/field[@name='uniqueId']"))
        element_add = self.solr.update_raw.call_args_list[2][0][0]
        self.assertEquals(
            ['http://xml.zeit.de/video/2010-03/6789'],
            element_add.xpath("/add/doc/field[@name='uniqueId']"))
        element_add = self.solr.update_raw.call_args_list[3][0][0]
        self.assertEquals(
            ['http://xml.zeit.de/video/playlist/2345'],
            element_add.xpath("/add/doc/field[@name='uniqueId']"))
        element_add = self.solr.update_raw.call_args_list[4][0][0]
        self.assertEquals(
            ['http://xml.zeit.de/video/playlist/3456'],
            element_add.xpath("/add/doc/field[@name='uniqueId']"))

    def test_deleted_playlists_removed_from_solr(self):
        pls = self.repository['playlist-2345']
        pls.item_state = 'DELETED'
        zope.lifecycleevent.modified(pls)
        self.assertTrue(self.solr.delete.called)
        self.assertTrue(self.public_solr.delete.called)

    def test_active_videos_should_be_index(self):
        video = zeit.cms.interfaces.ICMSContent(
            "http://xml.zeit.de/video/2010-03/1234")
        video.item_state = 'ACTIVE'
        zope.lifecycleevent.modified(video)
        self.assertTrue(self.solr.update_raw.called)
        self.assertTrue(self.public_solr.update_raw.called)

    def test_inactive_videos_should_be_deleted_from_solr(self):
        video = zeit.cms.interfaces.ICMSContent(
            "http://xml.zeit.de/video/2010-03/1234")
        video.item_state = 'INACTIVE'
        zope.lifecycleevent.modified(video)
        self.assertTrue(self.solr.delete.called)
        self.assertTrue(self.public_solr.delete.called)

    def test_deleted_videos_should_be_deleted_from_solr(self):
        video = zeit.cms.interfaces.ICMSContent(
            "http://xml.zeit.de/video/2010-03/1234")
        video.item_state = 'DELETED'
        zope.lifecycleevent.modified(video)
        self.assertTrue(self.solr.delete.called)
        self.assertTrue(self.public_solr.delete.called)
