# coding: utf-8
import argparse
import logging
import urllib.parse

import grokcore.component as grok
import requests
import zope.app.appsetup.product
import zope.interface

from zeit.push.interfaces import ISocialConfig, SocialConfig
import zeit.push.interfaces
import zeit.push.message


log = logging.getLogger(__name__)


@grok.implementer(ISocialConfig)
class FacebookConfig(SocialConfig):
    product_configuration = 'zeit.push'
    type = 'facebook'

    def __init__(self, account):
        self.account = account

    @property
    def token(self):
        return self.config(f'{self.type}-{self.account}-token')

    @property
    def name(self):
        return self.config(f'{self.type}-{self.account}-account')


accounts = ['main', 'magazin', 'campus', 'zett']
for account_name in accounts:
    grok.global_utility(
        FacebookConfig(account_name), provides=ISocialConfig, name=f'fb-{account_name}', direct=True
    )


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
class Connection:
    def __init__(self, url):
        self.url = url

    def send(self, text, link, **kw):
        account = kw['account']
        access_token = 'invalid'
        log.debug('Sending %s, %s to %s', text, link, account)
        if config := FacebookConfig.from_account_name(account):
            access_token = config.token
        self._request(
            'POST', '/me/feed', access_token, params={'message': text.encode('utf-8'), 'link': link}
        )

    def _request(self, method, path, access_token, **kw):
        kw.setdefault('params', {})['access_token'] = access_token
        http = requests.Session()
        try:
            func = getattr(http, method.lower())
            r = func(self.url + path, **kw)
            if not r.ok:
                r.reason = '%s (%s)' % (r.reason, r.text)
            r.raise_for_status()

            data = r.json()
            if 'error' in data:
                # XXX Don't know how to differentiate technical/semantic errors
                raise zeit.push.interfaces.TechnicalError(str(data['error']))
            return data
        except requests.exceptions.RequestException as e:
            raise zeit.push.interfaces.TechnicalError(str(e))
        finally:
            http.close()


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
def from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.push')
    return Connection(config['facebook-base-url'].rstrip('/'))


class Message(zeit.push.message.Message):
    grok.name('facebook')

    @property
    def text(self):
        return self.config.get('override_text')

    @property
    def url(self):
        return self.add_query_params(
            super().url,
            wt_zmc='sm.int.zonaudev.facebook.ref.zeitde.redpost.link.x',
            utm_medium='sm',
            utm_source='facebook_zonaudev_int',
            utm_campaign='ref',
            utm_content='zeitde_redpost_link_x',
        )

    @property
    def log_message_details(self):
        return 'Account %s' % self.config.get('account', '-')


def create_access_token(argv=None):
    parser = argparse.ArgumentParser(description='Create Facebook access token')
    parser.add_argument('--app-id', help='Application ID', default='638028906281625')
    parser.add_argument('--app-secret', help='Application Secret')
    parser.add_argument('--page-name', help='Name of the page', default='ZEIT ONLINE')
    options = parser.parse_args(argv)
    if not all([options.app_id, options.app_secret, options.page_name]):
        parser.print_help()
        raise SystemExit(1)
    options.redirect_uri = 'https://vivi.zeit.de/@@ping'

    # Step 1: Get user token. <https://developers.facebook.com
    # /docs/facebook-login/manually-build-a-login-flow#login>
    scopes = ','.join(
        [
            'pages_read_engagement',
            'pages_manage_posts',
            'business_management',
            'pages_manage_metadata',
            'pages_show_list',
        ]
    )
    login_url = 'https://www.facebook.com/dialog/oauth?' + urllib.parse.urlencode(
        {
            'client_id': options.app_id,
            'redirect_uri': options.redirect_uri,
            'scope': scopes,
        }
    )
    print('Bitte bei Facebook anmelden und dann diese URL öffnen:\n%s' % (login_url))
    print('Nach der Bestätigung der Berechtigungen erfolgt eine Weiterleitung,')
    result_url = input('die neue URL bitte hier eingeben: ')
    code = urllib.parse.parse_qs(urllib.parse.urlparse(result_url).query)['code'][0]

    # Step 1b: Convert code to token <https://developers.facebook.com
    # /docs/facebook-login/manually-build-a-login-flow#confirm>
    r = requests.get(
        'https://graph.facebook.com/oauth/access_token?'
        + urllib.parse.urlencode(
            {
                'client_id': options.app_id,
                'client_secret': options.app_secret,
                'redirect_uri': options.redirect_uri,
                'code': code,
            }
        )
    )
    if 'error' in r.text:
        print(r.text)
        raise SystemExit(1)
    short_lived_user_token = r.json()['access_token']

    # Step 2: Exchange for long-lived token. <https://developers.facebook.com
    # /docs/facebook-login/access-tokens/#extending>
    r = requests.get(
        'https://graph.facebook.com/oauth/access_token?'
        + urllib.parse.urlencode(
            {
                'client_id': options.app_id,
                'client_secret': options.app_secret,
                'grant_type': 'fb_exchange_token',
                'fb_exchange_token': short_lived_user_token,
            }
        )
    )
    if 'error' in r.text:
        print(r.text)
        raise SystemExit(1)
    long_lived_user_token = r.json()['access_token']
    print('Das User Token ist: %s' % long_lived_user_token)

    # Step 3. Retrieve page access token. <https://developers.facebook.com
    # /docs/facebook-login/access-tokens/#pagetokens>
    #
    # Note: Since we used a long-lived user token, the page token will be
    # long-lived (~60 days), too.
    r = requests.get(
        'https://graph.facebook.com/me/accounts', params={'access_token': long_lived_user_token}
    )
    if 'error' in r.text:
        print(r.text)
        raise SystemExit(1)
    page_token = [x['access_token'] for x in r.json()['data'] if x['name'] == options.page_name][0]

    print('Das Page Token für %s ist: %s' % (options.page_name, page_token))
