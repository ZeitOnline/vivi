from zeit.push.interfaces import twitterAccountSource
import argparse
import grokcore.component as grok
import logging
import tweepy
import zeit.push.interfaces
import zeit.push.message
import zope.interface


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
class Connection:

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def send(self, text, link, **kw):
        account = kw['account']
        access_token, access_secret = (
            twitterAccountSource.factory.access_token(account))

        auth = tweepy.OAuth1UserHandler(self.api_key, self.api_secret)
        auth.set_access_token(access_token, access_secret)
        api = tweepy.API(auth)

        log.debug('Sending %s, %s to %s', text, link, account)
        try:
            api.update_status('%s %s' % (text, link))
        except tweepy.HTTPException as e:
            status = e.response.status_code
            if status < 500:
                raise zeit.push.interfaces.WebServiceError(str(e))
            else:
                raise zeit.push.interfaces.TechnicalError(str(e))


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
def from_product_config():
    # soft dependency
    import zope.app.appsetup.product
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.push')
    return Connection(
        config['twitter-application-id'], config['twitter-application-secret'])


class Message(zeit.push.message.Message):

    grok.name('twitter')

    @property
    def text(self):
        text = self.config.get('override_text')
        if not text:  # BBB
            self.get_text_from = 'short_text'
            text = super().text
        return text

    @property
    def url(self):
        return self.add_query_params(
            super().url,
            wt_zmc='sm.int.zonaudev.twitter.ref.zeitde.redpost.link.x',
            utm_medium='sm',
            utm_source='twitter_zonaudev_int',
            utm_campaign='ref',
            utm_content='zeitde_redpost_link_x',
        )

    @property
    def log_message_details(self):
        return 'Account %s' % self.config.get('account', '-')


def create_access_token(argv=None):
    parser = argparse.ArgumentParser(
        description='Create Twitter access token')
    parser.add_argument('--app-key', help='Application Key')
    parser.add_argument('--app-secret', help='Application Secret')
    options = parser.parse_args(argv)
    if not all([options.app_key, options.app_secret]):
        parser.print_help()
        raise SystemExit(1)

    oauth = tweepy.OAuth1UserHandler(
        options.app_key, options.app_secret,
        # https://developer.twitter.com/en/docs/authentication
        #   /oauth-1-0a/pin-based-oauth
        callback='oob')
    login_url = oauth.get_authorization_url()
    print('Bitte bei Twitter anmelden und dann diese URL öffnen:\n%s' % (
        login_url))
    pin = input('Die von Twitter angezeigte PIN bitte hier eingeben: ')
    token, secret = oauth.get_access_token(pin)
    print(f'Token: {token}\nSecret: {secret}')
