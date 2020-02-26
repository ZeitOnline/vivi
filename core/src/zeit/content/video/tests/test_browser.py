import plone.testing
import zeit.cms.browser.interfaces
import zeit.cms.workflow.interfaces
import zeit.content.video.testing
import zeit.push.interfaces
import zeit.push.testing
import zope.component
import zope.publisher.browser
from zeit.content.image.testing import create_image_group_with_master_image


class TestThumbnail(zeit.content.video.testing.BrowserTestCase):

    def test_view_on_video_should_redirect_to_video_thumbnail_url(self):
        player = zope.component.getUtility(
            zeit.content.video.interfaces.IPlayer)
        player.get_video.return_value = {
            'renditions': (),
            'thumbnail': 'http://thumbnailurl',
            'video_still': None,
        }
        factory = zeit.content.video.testing.video_factory(self)
        next(factory)
        next(factory)
        self.browser.open('http://localhost/++skin++vivi/repository/video/')
        self.browser.follow_redirects = False
        self.browser.open('@@thumbnail')
        self.assertEqual('http://localhost/group/thumbnail',
                         self.browser.headers.get('location'))

    def test_url_of_view_on_video_should_return_thumbnail_url(self):
        player = zope.component.getUtility(
            zeit.content.video.interfaces.IPlayer)
        player.get_video.return_value = {
            'renditions': (),
            'thumbnail': 'http://thumbnailurl',
            'video_still': None,
        }
        factory = zeit.content.video.testing.video_factory(self)
        next(factory)
        video = next(factory)

        request = zope.publisher.browser.TestRequest(
            skin=zeit.cms.browser.interfaces.ICMSLayer)
        thumbnail_view = zope.component.getMultiAdapter(
            (video, request), name='thumbnail')
        url = zope.component.getMultiAdapter(
            (thumbnail_view, request),
            zope.traversing.browser.interfaces.IAbsoluteURL)()
        self.assertEqual(url, '/group/thumbnail')

    def test_view_on_playlist_should_redirect_to_playlist_thumbnail_url(self):
        factory = zeit.content.video.testing.playlist_factory(self)
        playlist = next(factory)
        playlist.thumbnail = create_image_group_with_master_image()
        next(factory)
        self.browser.open('http://localhost/++skin++vivi/repository/pls/')
        self.browser.follow_redirects = False
        self.browser.open('@@thumbnail')
        self.assertEqual('http://localhost/group/thumbnail',
                         self.browser.headers.get('location'))

    def test_url_of_view_on_playlist_should_return_thumbnail_url(self):
        factory = zeit.content.video.testing.playlist_factory(self)
        playlist = next(factory)
        playlist.thumbnail = create_image_group_with_master_image()
        playlist = next(factory)

        request = zope.publisher.browser.TestRequest(
            skin=zeit.cms.browser.interfaces.ICMSLayer)
        thumbnail_view = zope.component.getMultiAdapter(
            (playlist, request), name='thumbnail')
        url = zope.component.getMultiAdapter(
            (thumbnail_view, request),
            zope.traversing.browser.interfaces.IAbsoluteURL)()
        self.assertEqual(url, '/group/thumbnail')


class TestStill(zeit.content.video.testing.BrowserTestCase):

    def test_preview_view_on_video_should_redirect_to_still_url(self):
        factory = zeit.content.video.testing.video_factory(self)
        player = zope.component.getUtility(
            zeit.content.video.interfaces.IPlayer)
        player.get_video.return_value = {
            'renditions': (),
        }
        next(factory)
        next(factory)
        self.browser.open('http://localhost/++skin++vivi/repository/video/')
        self.browser.follow_redirects = False
        self.browser.open('@@preview')
        self.assertEqual('http://localhost/group/small',
                         self.browser.headers.get('location'))

    def test_url_of_preview_view_on_video_should_return_still_url(self):
        player = zope.component.getUtility(
            zeit.content.video.interfaces.IPlayer)
        player.get_video.return_value = {
            'renditions': (),
        }
        factory = zeit.content.video.testing.video_factory(self)
        next(factory)
        video = next(factory)

        request = zope.publisher.browser.TestRequest(
            skin=zeit.cms.browser.interfaces.ICMSLayer)
        view = zope.component.getMultiAdapter(
            (video, request), name='preview')
        url = zope.component.getMultiAdapter(
            (view, request),
            zope.traversing.browser.interfaces.IAbsoluteURL)()
        self.assertEqual(url, '/group/small')


class TestPlaylist(zeit.content.video.testing.BrowserTestCase):

    def test_playlist_should_be_viewable(self):
        from zeit.content.video.playlist import Playlist
        self.repository['453'] = Playlist()
        self.browser.open('http://localhost/++skin++vivi/repository/453')
        self.assert_ellipsis("""...
<...
   <label for="form.__name__">
           <span>File name</span>
         </label>...
        <div class="widget">453</div>...
                             """)


VIDEO_PUSHMOCK_WSGI_LAYER = plone.testing.Layer(
    bases=(zeit.content.video.testing.WSGI_LAYER,
           zeit.push.testing.PUSH_MOCK_LAYER),
    name='VideoPushMockLayer')


class TestVideoEdit(zeit.content.video.testing.BrowserTestCase):
    """Testing ..browser.video.Edit."""

    layer = VIDEO_PUSHMOCK_WSGI_LAYER

    def test_push_to_social_media_is_done_on_publish(self):
        factory = zeit.content.video.testing.video_factory(self)
        video = next(factory)
        video.title = u'My video'
        video.ressort = u'Deutschland'
        video = next(factory)
        browser = self.browser
        browser.open('http://localhost/++skin++vivi/repository/video')
        browser.getLink('Checkout').click()
        browser.getControl('Short push text').value = 'See this video!'
        browser.getControl('Enable Twitter', index=0).click()
        browser.getControl('Apply').click()
        self.assertIn('Updated on', browser.contents)
        browser.getLink('Checkin').click()
        self.assertIn('"video" has been checked in.', browser.contents)
        zeit.cms.workflow.interfaces.IPublish(video).publish(background=False)
        twitter = zope.component.getUtility(
            zeit.push.interfaces.IPushNotifier, name='twitter')
        self.assertEqual(
            u'See this video!', twitter.calls[0][0])
        self.assertEqual(
            u'http://www.zeit.de/video/my-video', twitter.calls[0][1])
        params = twitter.calls[0][2]
        del params['message']
        self.assertEqual(
            {'enabled': True, 'account': 'twitter-test', 'type': 'twitter'},
            params)
