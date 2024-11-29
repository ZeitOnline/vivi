import zope.component
import zope.publisher.browser

import zeit.cms.browser.interfaces
import zeit.cms.workflow.interfaces
import zeit.content.video.testing


class TestStill(zeit.content.video.testing.BrowserTestCase):
    def test_preview_view_on_video_should_redirect_to_still_url(self):
        factory = zeit.content.video.testing.video_factory(self)
        player = zope.component.getUtility(zeit.content.video.interfaces.IPlayer)
        player.get_video.return_value = {
            'renditions': (),
            'video_still': 'http://stillurl',
        }
        next(factory)
        next(factory)
        self.browser.open('http://localhost/++skin++vivi/repository/video/')
        self.browser.follow_redirects = False
        self.browser.open('@@preview')
        self.assertEqual('http://stillurl', self.browser.headers.get('location'))

    def test_url_of_preview_view_on_video_should_return_still_url(self):
        player = zope.component.getUtility(zeit.content.video.interfaces.IPlayer)
        player.get_video.return_value = {
            'renditions': (),
            'video_still': 'http://stillurl',
        }
        factory = zeit.content.video.testing.video_factory(self)
        next(factory)
        video = next(factory)

        request = zope.publisher.browser.TestRequest(skin=zeit.cms.browser.interfaces.ICMSLayer)
        view = zope.component.getMultiAdapter((video, request), name='preview')
        url = zope.component.getMultiAdapter(
            (view, request), zope.traversing.browser.interfaces.IAbsoluteURL
        )()
        self.assertEqual(url, 'http://stillurl')
