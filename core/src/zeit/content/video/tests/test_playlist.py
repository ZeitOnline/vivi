# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.video.testing


class TestPlaylist(zeit.content.video.testing.TestCase):

    def test_videos_should_contain_metadata_in_xml(self):
        factory = zeit.content.video.testing.video_factory(self)
        video = factory.next()
        video.teaserText = u'Bla bla'
        video = factory.next()  # in repository
        factory = zeit.content.video.testing.playlist_factory(self)
        pls = factory.next()
        pls.videos = (video,)
        self.assertEqual(
            u'Bla bla', pls.xml['body']['videos']['video']['text'])

    def test_video_title_should_show_up_as_teaser_title_in_playlist(self):
        factory = zeit.content.video.testing.video_factory(self)
        video = factory.next()
        video.title = u'The big Foo'
        video = factory.next()  # in repository
        factory = zeit.content.video.testing.playlist_factory(self)
        pls = factory.next()
        pls.videos = (video,)
        self.assertEqual(
            u'The big Foo', pls.xml['body']['videos']['video']['title'])

    def test_security_should_allow_access_to_id_prefix(self):
        import zeit.cms.testing
        import zope.security.management
        from zope.security.proxy import ProxyFactory
        factory = zeit.content.video.testing.playlist_factory(self)
        factory.next()
        pls = factory.next()  # in repository
        zope.security.management.endInteraction()
        with zeit.cms.testing.interaction('zope.mgr'):
            proxied = ProxyFactory(pls)
            self.assertEqual('pls', proxied.id_prefix)

    def test_playlist_should_update_video_metadata_on_checkin(self):
        factory = zeit.content.video.testing.video_factory(self)
        video = factory.next()
        video.title = u'foo'
        video = factory.next()  # in repository
        factory = zeit.content.video.testing.playlist_factory(self)
        pls = factory.next()
        pls.videos = (video,)
        pls = factory.next()  # in repository
        with zeit.cms.checkout.helper.checked_out(video) as co:
            co.title = u'bar'
        with zeit.cms.checkout.helper.checked_out(pls):
            pass
        pls = self.repository['pls']
        self.assertEqual(
            u'bar', pls.xml['body']['videos']['video']['title'])


class TestReferencesAdapter(zeit.content.video.testing.TestCase):

    def test_playlist_references_should_contain_its_videos(self):
        factory = zeit.content.video.testing.video_factory(self)
        video = factory.next()
        video.teaserText = u'Bla bla'
        video = factory.next()  # in repository
        factory = zeit.content.video.testing.playlist_factory(self)
        pls = factory.next()
        pls.videos = (video,)

        videos = zeit.cms.relation.interfaces.IReferences(pls)
        self.assertEqual(1, len(videos))
        self.assertEquals(
            'http://xml.zeit.de/video', videos[0].uniqueId)
