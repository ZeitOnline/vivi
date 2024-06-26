import plone.testing
import zope.component
import zope.publisher.browser

import zeit.cms.browser.interfaces
import zeit.cms.workflow.interfaces
import zeit.content.video.testing
import zeit.push.interfaces
import zeit.push.testing


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


VIDEO_PUSHMOCK_WSGI_LAYER = plone.testing.Layer(
    bases=(zeit.content.video.testing.WSGI_LAYER, zeit.push.testing.PUSH_MOCK_LAYER),
    name='VideoPushMockLayer',
)


class TestVideoEdit(zeit.content.video.testing.BrowserTestCase):
    """Testing ..browser.video.Edit."""

    layer = VIDEO_PUSHMOCK_WSGI_LAYER

    def test_push_to_social_media_is_done_on_publish(self):
        factory = zeit.content.video.testing.video_factory(self)
        video = next(factory)
        video.title = 'My video'
        video.ressort = 'Deutschland'
        video = next(factory)
        browser = self.browser
        browser.open('http://localhost/++skin++vivi/repository/video')
        browser.getLink('Checkout').click()
        browser.getControl('Enable mobile push').selected = True
        browser.getControl('Mobile title').value = 'mobile title'
        browser.getControl('Mobile text').value = 'See this video!'
        browser.getControl('Payload Template').value = 'foo.json'
        browser.getControl('Apply').click()
        browser.getLink('Checkin').click()
        self.assertIn('"video" has been checked in.', browser.contents)
        zeit.cms.workflow.interfaces.IPublish(video).publish(background=False)
        push = zope.component.getUtility(zeit.push.interfaces.IPushNotifier, 'urbanairship')
        self.assertEqual('See this video!', push.calls[0][0])
        self.assertIn('http://www.zeit.de/video/my-video', push.calls[0][1])
        params = push.calls[0][2]
        del params['message']
        self.assertEqual(
            {
                'enabled': 1,
                'override_text': 'See this video!',
                'payload_template': 'foo.json',
                'title': 'mobile title',
                'type': 'mobile',
                'uses_image': 0,
                'variant': 'manual',
            },
            params,
        )
