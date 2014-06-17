import time
import fb
import zeit.push.testing
import zeit.push.facebook


class FacebookTest(zeit.push.testing.TestCase):

    level = 2

    # User: tl+facebooktest@gocept.com
    # Pass: FiN7XHSx
    # app_id = '492113357602143'
    # app_secret = '7a1c8fbc7250d7b58103882368db33aa'
    #
    # Page access token for
    # <https://www.facebook.com/pages/Vivi-Test/721128357931123>,
    # created on 2014-07-16, expires in about 60 days, recreate with
    # ./work/maintenancejobs/bin/facebook-access-token
    access_token = (
        'CAAGZCkxHefV8BAFx0CjyFY8hYn5dd0vKJh0NPOSLQxkR4jYQtwbu3QQvNzglDqyp26E6'
        'zCgX4LDsmpZChrBWAUa8r4l1cLCCfAExjvTyKRbucS1jo2ng4xpErMxKQOXHpdmZCziU6'
        'Ar9zZAuswmLZBhGiq0JV8qJBUaTkPjEciQq2BoYUZARQQ')

    def setUp(self):
        self.api = fb.graph.api(self.access_token)
        # repr keeps all digits  while str would cut them.
        self.nugget = repr(time.time())

    def tearDown(self):
        for status in self.api.get_object(
                cat='single', id='me', fields=['feed'])['feed']['data']:
            if 'message' in status and self.nugget in status['message']:
                self.api.delete(id=status['id'])

    def test_send_posts_status(self):
        facebook = zeit.push.facebook.Connection()
        facebook.send(
            'zeit.push.tests.facebook %s' % self.nugget, 'http://example.com',
            account='fb-test')

        for status in self.api.get_object(
                cat='single', id='me', fields=['feed'])['feed']['data']:
            if self.nugget in status['message']:
                self.assertEqual('http://example.com/', status['link'])
                break
        else:
            self.fail('Status was not posted')

    def test_errors_should_raise(self):
        facebook = zeit.push.facebook.Connection()
        with self.assertRaises(zeit.push.interfaces.TechnicalError) as e:
            facebook.send('foo', '', account='fb_ressort_deutschland')
        self.assertIn('Invalid OAuth access token.', e.exception.message)


class FacebookAccountsTest(zeit.push.testing.TestCase):

    def test_main_account_is_excluded_from_source(self):
        self.assertEqual(
            ['fb_ressort_deutschland', 'fb_ressort_international'],
            list(zeit.push.facebook.facebookAccountSource(None)))
