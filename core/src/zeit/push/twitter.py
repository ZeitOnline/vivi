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

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def send(self, text, link, **kw):
        account = kw['account']
        access_token, _ = twitterAccountSource.factory.access_token(account)
        api = tweepy.Client(access_token)

        log.debug('Sending %s, %s to %s', text, link, account)
        try:
            api.create_tweet(text=f'{text} {link}', user_auth=False)
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
    parser.add_argument('--client-id', help='OAuth2 Client ID')
    parser.add_argument('--client-secret', help='OAuth2 Client Secret')
    options = parser.parse_args(argv)
    if not all([options.client_id, options.client_secret]):
        parser.print_help()
        raise SystemExit(1)

    oauth = tweepy.OAuth2UserHandler(
        client_id=options.client_id,
        redirect_uri='https://vivi.zeit.de/@@ping',
        # https://developer.twitter.com/en/docs/authentication
        #   /guides/v2-authentication-mapping
        scope=['tweet.write', 'tweet.read', 'users.read', 'offline.access'],
        client_secret=options.client_secret)
    login_url = oauth.get_authorization_url()
    print('Bitte bei Twitter anmelden und dann diese URL öffnen:\n%s' % (
        login_url))
    print(
        'Nach der Bestätigung der Berechtigungen erfolgt eine Weiterleitung,')
    result_url = input('die neue URL bitte hier eingeben: ')

    token = oauth.fetch_token(result_url)
    print('Das Token ist: %s' % token)
