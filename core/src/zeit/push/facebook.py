# coding: utf-8
from six.moves import input
from zeit.push.interfaces import facebookAccountSource
import argparse
import fb
import grokcore.component as grok
import logging
import requests
import six.moves.urllib.parse
import zeit.push.interfaces
import zeit.push.message
import zope.interface


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
class Connection(object):

    def send(self, text, link, **kw):
        account = kw['account']
        access_token = facebookAccountSource.factory.access_token(account)

        breaking = ' breaking_news=true' if kw.get('breaking_news') else ''
        log.debug('Sending %s, %s to %s%s', text, link, account, breaking)
        fb_api = fb.graph.api(access_token)
        params = {}
        if kw.get('breaking_news'):
            config = zope.app.appsetup.product.getProductConfiguration(
                'zeit.push')
            params['breaking_news'] = True
            params['breaking_news_expiration'] = int(
                config['facebook-breaking-news-expiration'])

        result = fb_api.publish(
            cat='feed', id='me', message=text.encode('utf-8'), link=link,
            **params)
        if 'error' in result:
            if result['error'].get('code') == 200 and kw.get('breaking_news'):
                log.info(
                    'Sending %s with breaking_news failed, retrying without',
                    link)
                kw.pop('breaking_news')
                return self.send(text, link, **kw)
            # XXX Don't know how to differentiate technical and semantic errors
            raise zeit.push.interfaces.TechnicalError(str(result['error']))


class Message(zeit.push.message.Message):

    grok.name('facebook')

    @property
    def text(self):
        text = self.config.get('override_text')
        if not text:  # BBB
            self.get_text_from = 'long_text'
            text = super(Message, self).text
        return text

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

    def _disable_message_config(self):
        push = zeit.push.interfaces.IPushMessages(self.context)
        if self.config.get('breaking_news'):
            push.set(self.config, enabled=False, breaking_news=False)
        else:
            push.set(self.config, enabled=False)


def create_access_token(argv=None):
    parser = argparse.ArgumentParser(
        description='Create Facebook access token')
    parser.add_argument('--app-id', help='Application ID',
                        default='638028906281625')
    parser.add_argument('--app-secret', help='Application Secret')
    parser.add_argument('--page-name', help='Name of the page',
                        default='ZEIT ONLINE')
    options = parser.parse_args(argv)
    if not all([options.app_id, options.app_secret, options.page_name]):
        parser.print_help()
        raise SystemExit(1)
    options.redirect_uri = 'https://vivi.zeit.de/@@ping'

    # Step 1: Get user token. <https://developers.facebook.com
    # /docs/facebook-login/manually-build-a-login-flow#login>
    scopes = ','.join([
        'pages_read_engagement',
        'pages_manage_posts',
        'business_management',
        'pages_manage_metadata',
        'pages_show_list'
    ])
    login_url = ('https://www.facebook.com/dialog/oauth?' +
                 six.moves.urllib.parse.urlencode({
                     'client_id': options.app_id,
                     'redirect_uri': options.redirect_uri,
                     'scope': scopes,
                 }))
    print(u'Bitte bei Facebook anmelden und dann diese URL öffnen:\n%s' % (
        login_url))
    print(
        u'Nach der Bestätigung der Berechtigungen erfolgt eine Weiterleitung,')
    result_url = input('die neue URL bitte hier eingeben: ')
    code = six.moves.urllib.parse.parse_qs(
        six.moves.urllib.parse.urlparse(result_url).query)['code'][0]

    # Step 1b: Convert code to token <https://developers.facebook.com
    # /docs/facebook-login/manually-build-a-login-flow#confirm>
    r = requests.get(
        'https://graph.facebook.com/oauth/access_token?' +
        six.moves.urllib.parse.urlencode({
            'client_id': options.app_id,
            'client_secret': options.app_secret,
            'redirect_uri': options.redirect_uri,
            'code': code,
        }))
    if 'error' in r.text:
        print(r.text)
        raise SystemExit(1)
    short_lived_user_token = r.json()['access_token']

    # Step 2: Exchange for long-lived token. <https://developers.facebook.com
    # /docs/facebook-login/access-tokens/#extending>
    r = requests.get(
        'https://graph.facebook.com/oauth/access_token?' +
        six.moves.urllib.parse.urlencode({
            'client_id': options.app_id,
            'client_secret': options.app_secret,
            'grant_type': 'fb_exchange_token',
            'fb_exchange_token': short_lived_user_token,
        }))
    if 'error' in r.text:
        print(r.text)
        raise SystemExit(1)
    long_lived_user_token = r.json()['access_token']
    print(u'Das User Token ist: %s' % long_lived_user_token)

    # Step 3. Retrieve page access token. <https://developers.facebook.com
    # /docs/facebook-login/access-tokens/#pagetokens>
    #
    # Note: Since we used a long-lived user token, the page token will be
    # long-lived (~60 days), too.
    user = fb.graph.api(long_lived_user_token)
    accounts = user.get_object(cat='single', id='me', fields=['accounts'])
    page_token = [x['access_token'] for x in accounts['accounts']['data']
                  if x['name'] == options.page_name][0]

    print(u'Das Page Token für %s ist: %s' % (options.page_name, page_token))
