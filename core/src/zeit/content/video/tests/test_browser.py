# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing
import zeit.content.video.testing


class TestThumbnail(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.video.testing.Layer

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

    layer = zeit.content.video.testing.Layer

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

    layer = zeit.content.video.testing.Layer

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
