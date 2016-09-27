import plone.testing
import zeit.push.interfaces
import zeit.cms.testing
import zeit.cms.workflow.interfaces
import zeit.content.video.testing
import zeit.push.testing
import zope.component
import zope.security.management


class TestThumbnail(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.video.testing.LAYER

    def test_view_on_video_should_redirect_to_video_thumbnail_url(self):
        import urllib2
        factory = zeit.content.video.testing.video_factory(self)
        video = factory.next()
        video.thumbnail = 'http://thumbnailurl'
        factory.next()
        self.browser.open('http://localhost/++skin++vivi/repository/video/')
        self.browser.mech_browser.set_handle_redirect(False)
        with self.assertRaises(urllib2.HTTPError) as e:
            self.browser.open('@@thumbnail')
        self.assertEqual('HTTP Error 303: See Other', str(e.exception))
        self.assertEqual('http://thumbnailurl',
                         e.exception.hdrs.get('location'))

    def test_url_of_view_on_video_should_return_thumbnail_url(self):
        import zope.publisher.browser
        import zope.component
        import zeit.cms.browser.interfaces
        factory = zeit.content.video.testing.video_factory(self)
        video = factory.next()
        video.thumbnail = 'http://thumbnailurl'
        video = factory.next()

        request = zope.publisher.browser.TestRequest(
            skin=zeit.cms.browser.interfaces.ICMSLayer)
        with zeit.cms.testing.site(self.getRootFolder()):
            thumbnail_view = zope.component.getMultiAdapter(
                (video, request), name='thumbnail')
            url = zope.component.getMultiAdapter(
                (thumbnail_view, request),
                zope.traversing.browser.interfaces.IAbsoluteURL)()
        self.assertEqual(url, 'http://thumbnailurl')

    def test_view_on_playlist_should_redirect_to_playlist_thumbnail_url(self):
        import urllib2
        factory = zeit.content.video.testing.playlist_factory(self)
        playlist = factory.next()
        playlist.thumbnail = 'http://thumbnailurl'
        factory.next()
        self.browser.open('http://localhost/++skin++vivi/repository/pls/')
        self.browser.mech_browser.set_handle_redirect(False)
        with self.assertRaises(urllib2.HTTPError) as e:
            self.browser.open('@@thumbnail')
        self.assertEqual('HTTP Error 303: See Other', str(e.exception))
        self.assertEqual('http://thumbnailurl',
                         e.exception.hdrs.get('location'))

    def test_url_of_view_on_playlist_should_return_thumbnail_url(self):
        import zope.publisher.browser
        import zope.component
        import zeit.cms.browser.interfaces
        factory = zeit.content.video.testing.playlist_factory(self)
        playlist = factory.next()
        playlist.thumbnail = 'http://thumbnailurl'
        playlist = factory.next()

        request = zope.publisher.browser.TestRequest(
            skin=zeit.cms.browser.interfaces.ICMSLayer)
        with zeit.cms.testing.site(self.getRootFolder()):
            thumbnail_view = zope.component.getMultiAdapter(
                (playlist, request), name='thumbnail')
            url = zope.component.getMultiAdapter(
                (thumbnail_view, request),
                zope.traversing.browser.interfaces.IAbsoluteURL)()
        self.assertEqual(url, 'http://thumbnailurl')


class TestStill(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.video.testing.LAYER

    def test_preview_view_on_video_should_redirect_to_still_url(self):
        import urllib2
        factory = zeit.content.video.testing.video_factory(self)
        video = factory.next()
        video.video_still = 'http://stillurl'
        factory.next()
        self.browser.open('http://localhost/++skin++vivi/repository/video/')
        self.browser.mech_browser.set_handle_redirect(False)
        with self.assertRaises(urllib2.HTTPError) as e:
            self.browser.open('@@preview')
        self.assertEqual('HTTP Error 303: See Other', str(e.exception))
        self.assertEqual('http://stillurl',
                         e.exception.hdrs.get('location'))

    def test_url_of_preview_view_on_video_should_return_still_url(self):
        import zope.publisher.browser
        import zope.component
        import zeit.cms.browser.interfaces
        factory = zeit.content.video.testing.video_factory(self)
        video = factory.next()
        video.video_still = 'http://stillurl'
        video = factory.next()

        request = zope.publisher.browser.TestRequest(
            skin=zeit.cms.browser.interfaces.ICMSLayer)
        with zeit.cms.testing.site(self.getRootFolder()):
            view = zope.component.getMultiAdapter(
                (video, request), name='preview')
            url = zope.component.getMultiAdapter(
                (view, request),
                zope.traversing.browser.interfaces.IAbsoluteURL)()
        self.assertEqual(url, 'http://stillurl')


class TestPlaylist(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.video.testing.LAYER

    def test_playlist_should_be_viewable(self):
        from zeit.content.video.playlist import Playlist
        pls = Playlist()
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                self.repository['453'] = pls
        self.browser.open('http://localhost/++skin++vivi/repository/453')
        self.assert_ellipsis("""...
<...
   <label for="form.__name__">
           <span>File name</span>
         </label>...
        <div class="widget">453</div>...
                             """)


VIDEO_PUSHMOCK_LAYER = plone.testing.Layer(
    bases=(zeit.content.video.testing.LAYER,
           zeit.push.testing.PUSH_MOCK_LAYER),
    name='VideoPushMockLayer')


class TestVideoEdit(zeit.cms.testing.BrowserTestCase):
    """Testing ..browser.video.Edit."""

    layer = VIDEO_PUSHMOCK_LAYER

    def test_push_to_social_media_is_done_on_publish(self):
        factory = zeit.content.video.testing.video_factory(self)
        video = factory.next()
        video.title = u'My video'
        video.ressort = u'Deutschland'
        video = factory.next()
        browser = self.browser
        browser.open('http://localhost/++skin++vivi/repository/video')
        browser.getLink('Checkout').click()
        browser.getControl('Short push text').value = 'See this video!'
        browser.getControl('Enable Twitter', index=0).click()
        browser.getControl('Apply').click()
        self.assertIn('Updated on', browser.contents)
        browser.getLink('Checkin').click()
        self.assertIn('"video" has been checked in.', browser.contents)
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                zeit.cms.workflow.interfaces.IPublish(video).publish(
                    async=False)
        twitter = zope.component.getUtility(
            zeit.push.interfaces.IPushNotifier, name='twitter')
        self.assertEqual([
            (u'See this video!',
             u'http://www.zeit.de/video/my-video',
             {'enabled': True, 'account': 'twitter-test', 'type': 'twitter'})],
            twitter.calls)
