from zeit.push.interfaces import ITwitterCredentials
import argparse
import grokcore.component as grok
import logging
import tweepy
import zeit.push.interfaces
import zeit.push.message
import zope.container.btree
import zope.interface


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
class Connection:

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def send(self, text, link, **kw):
        account = kw['account']
        api = TwitterClient(self.client_id, self.client_secret, account)
        log.debug('Sending %s, %s to %s', text, link, account)
        try:
            api.create_tweet(text=f'{text} {link}')
        except tweepy.HTTPException as e:
            status = e.response.status_code
            if status < 500:
                raise zeit.push.interfaces.WebServiceError(str(e))
            else:
                raise zeit.push.interfaces.TechnicalError(str(e))
        finally:
            api.session.close()


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
def from_product_config():
    # soft dependency
    import zope.app.appsetup.product
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.push')
    return Connection(
        config['twitter-application-id'], config['twitter-application-secret'])


class TwitterClient(tweepy.Client):

    # https://developer.twitter.com/en/docs/authentication
    #   /guides/v2-authentication-mapping
    scopes = ['tweet.write', 'tweet.read', 'users.read', 'offline.access']

    def __init__(self, client_id, client_secret, account_name):
        super().__init__()
        self.oauth = OAuth2UserHandler(
            client_id=client_id, client_secret=client_secret,
            redirect_uri='https://vivi.zeit.de/@@ping', scope=self.scopes)
        self.account_name = account_name

    def request(self, method, route, params=None, json=None, user_auth=False):
        user_auth = False  # Always use OAuth2, never OAuth1
        try:
            return super().request(method, route, params, json, user_auth)
        except tweepy.Unauthorized:
            self.refresh_token()
            return super().request(method, route, params, json, user_auth)

    def _get_authenticating_user_id(self, *, oauth_1=False):
        return super()._get_authenticating_user_id(oauth_1=False)

    @property
    def bearer_token(self):
        return zope.component.getUtility(ITwitterCredentials).access_token(
            self.account_name)

    @bearer_token.setter
    def bearer_token(self, value):
        pass  # superclass wants to write here, but we don't.

    def refresh_token(self):
        creds = zope.component.getUtility(ITwitterCredentials)
        # Note: This creates *both* a new access token and refresh token,
        # and thus invalidates the passed-in refresh token,
        # see https://twittercommunity.com/t/168899/42
        log.info('Refreshing tokens for %s', self.account_name)
        new = self.oauth.refresh_token(creds.refresh_token(self.account_name))
        creds.update(
            self.account_name, new['access_token'], new['refresh_token'])


class OAuth2UserHandler(tweepy.OAuth2UserHandler):
    """Adapted from https://github.com/tweepy/tweepy/discussions/1912
    to work for a "confidential client" application."""

    def refresh_token(self, refresh_token):
        return super().refresh_token(
            'https://api.twitter.com/2/oauth2/token',
            auth=self.auth,
            refresh_token=refresh_token,
            body='grant_type=refresh_token')


@zope.interface.implementer(zeit.push.interfaces.ITwitterCredentials)
class TwitterCredentials(zope.container.btree.BTreeContainer):

    def access_token(self, account_name):
        return self.get(account_name, {}).get('access')

    def refresh_token(self, account_name):
        return self.get(account_name, {}).get('refresh')

    def update(self, account_name, access_token, refresh_token):
        self[account_name] = {'access': access_token, 'refresh': refresh_token}


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
    parser.add_argument('--client-id', help='OAuth2 Client ID')
    parser.add_argument('--client-secret', help='OAuth2 Client Secret')
    options = parser.parse_args(argv)
    if not all([options.client_id, options.client_secret]):
        parser.print_help()
        raise SystemExit(1)

    oauth = TwitterClient(options.client_id, options.client_secret, None).oauth
    login_url = oauth.get_authorization_url()
    print('Bitte bei Twitter anmelden und dann diese URL öffnen:\n%s' % (
        login_url))
    print(
        'Nach der Bestätigung der Berechtigungen erfolgt eine Weiterleitung,')
    result_url = input('die neue URL bitte hier eingeben: ')

    token = oauth.fetch_token(result_url)
    print('Das Token ist: %s' % token)
