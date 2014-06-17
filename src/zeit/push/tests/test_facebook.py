import time
import fb
import zeit.push.testing
import zeit.push.facebook


class FacebookTest(zeit.push.testing.TestCase):

    level = 2

    # User: tl+facebooktest@gocept.com
    # Pass: FiN7XHSx
    app_id = '492113357602143'
    app_secret = '7a1c8fbc7250d7b58103882368db33aa'
    # Created on 2014-07-16, expires in about 60 days, recreate with
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
            account='testaccount')

        for status in self.api.get_object(
                cat='single', id='me', fields=['feed'])['feed']['data']:
            if self.nugget in status['message']:
                self.assertEqual('http://example.com/', status['link'])
                break
        else:
            self.fail('Status was not posted')
