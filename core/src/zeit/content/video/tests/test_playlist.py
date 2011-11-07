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


class TestReferencesAdapter(zeit.content.video.testing.TestCase):

    def test_should_contains(self):
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
