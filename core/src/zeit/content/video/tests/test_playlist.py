from zeit.cms.checkout.helper import checked_out
from zeit.cms.workflow.interfaces import IPublicationDependencies
import zeit.cms.workflow.interfaces
import zeit.content.animation.animation
import zeit.content.video.testing


class TestPlaylist(zeit.content.video.testing.TestCase):
    def test_videos_should_contain_metadata_in_xml(self):
        factory = zeit.content.video.testing.video_factory(self)
        video = next(factory)
        video.teaserText = 'Bla bla'
        video = next(factory)  # in repository
        factory = zeit.content.video.testing.playlist_factory(self)
        pls = next(factory)
        pls.videos = (video,)
        self.assertEqual('Bla bla', pls.xml.find('body/videos/video/text').text)

    def test_video_title_should_show_up_as_teaser_title_in_playlist(self):
        factory = zeit.content.video.testing.video_factory(self)
        video = next(factory)
        video.title = 'The big Foo'
        video = next(factory)  # in repository
        factory = zeit.content.video.testing.playlist_factory(self)
        pls = next(factory)
        pls.videos = (video,)
        self.assertEqual('The big Foo', pls.xml.find('body/videos/video/title').text)

    def test_security_should_allow_access_to_id_prefix(self):
        from zope.security.proxy import ProxyFactory
        import zope.security.management

        import zeit.cms.testing

        factory = zeit.content.video.testing.playlist_factory(self)
        next(factory)
        pls = next(factory)  # in repository
        zope.security.management.endInteraction()
        with zeit.cms.testing.interaction('zope.mgr'):
            proxied = ProxyFactory(pls)
            self.assertEqual('pls', proxied.id_prefix)

    def test_playlist_should_update_video_metadata_on_checkin(self):
        factory = zeit.content.video.testing.video_factory(self)
        video = next(factory)
        video.title = 'foo'
        video = next(factory)  # in repository
        factory = zeit.content.video.testing.playlist_factory(self)
        pls = next(factory)
        pls.videos = (video,)
        pls = next(factory)  # in repository
        with zeit.cms.checkout.helper.checked_out(video) as co:
            co.title = 'bar'
        with zeit.cms.checkout.helper.checked_out(pls):
            pass
        pls = self.repository['pls']
        self.assertEqual('bar', pls.xml.find('body/videos/video/title').text)

    def test_animation_video_reference(self):
        import zeit.content.animation.animation

        factory = zeit.content.video.testing.video_factory(self)
        next(factory)
        video = next(factory)
        animation = zeit.content.animation.animation.Animation()
        animation.video = video
        assert animation.xml.find('body/video').xpath('@contenttype')[0] == 'video'


class TestReferencesAdapter(zeit.content.video.testing.TestCase):
    def test_playlist_references_should_contain_its_videos(self):
        factory = zeit.content.video.testing.video_factory(self)
        video = next(factory)
        video.teaserText = 'Bla bla'
        video = next(factory)  # in repository
        factory = zeit.content.video.testing.playlist_factory(self)
        pls = next(factory)
        pls.videos = (video,)

        videos = zeit.cms.relation.interfaces.IReferences(pls)
        self.assertEqual(1, len(videos))
        self.assertEqual('http://xml.zeit.de/video', videos[0].uniqueId)

    def test_playlist_is_published_when_contained_video_is_published(self):
        factory = zeit.content.video.testing.video_factory(self)
        video = next(factory)
        video = next(factory)  # in repository
        factory = zeit.content.video.testing.playlist_factory(self)
        pls = next(factory)
        pls.videos = (video,)
        pls = next(factory)  # in repository
        self.assertIn(pls, IPublicationDependencies(video).get_dependencies())

    def test_non_playlist_referencing_content_not_published_with_video(self):
        factory = zeit.content.video.testing.video_factory(self)
        video = next(factory)
        video = next(factory)  # in repository

        with checked_out(self.repository['testcontent']) as co:
            zeit.cms.related.interfaces.IRelatedContent(co).related = (video,)

        self.assertNotIn(
            self.repository['testcontent'], IPublicationDependencies(video).get_dependencies()
        )
