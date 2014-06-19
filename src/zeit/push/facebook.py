# coding: utf-8
import argparse
import fb
import grokcore.component as grok
import requests
import urllib
import urlparse
import xml.sax.saxutils
import zc.sourcefactory.source
import zeit.cms.content.sources
import zeit.push.interfaces
import zeit.push.message
import zope.interface


class Connection(object):

    zope.interface.implements(zeit.push.interfaces.IPushNotifier)

    def send(self, text, link, **kw):
        account = kw['account']
        access_token = facebookAccountSource.factory.access_token(account)

        fb_api = fb.graph.api(access_token)
        result = fb_api.publish(
            cat='feed', id='me', message=text, link=link)
        if 'error' in result:
            # XXX Don't know how to differentiate technical and semantic errors
            raise zeit.push.interfaces.TechnicalError(str(result['error']))


class FacebookAccountSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.push'
    config_url = 'facebook-accounts'
    attribute = 'name'

    class source_class(zc.sourcefactory.source.FactoredContextualSource):

        @property
        def MAIN_ACCOUNT(self):
            return self.factory.main_account()

        @property
        def MAGAZIN_ACCOUNT(self):
            return self.factory.magazin_account()

    @classmethod
    def main_account(cls):
        config = zope.app.appsetup.product.getProductConfiguration(
            cls.product_configuration)
        return config['facebook-main-account']

    @classmethod
    def magazin_account(cls):
        config = zope.app.appsetup.product.getProductConfiguration(
            cls.product_configuration)
        return config['facebook-magazin-account']

    def isAvailable(self, node, context):
        return (super(FacebookAccountSource, self).isAvailable(node, context)
                and node.get('name') != self.main_account())

    def access_token(self, value):
        tree = self._get_tree()
        nodes = tree.xpath('%s[@%s= %s]' % (
                           self.title_xpath,
                           self.attribute,
                           xml.sax.saxutils.quoteattr(value)))
        if not nodes:
            return (None, None)
        node = nodes[0]
        return node.get('token')

facebookAccountSource = FacebookAccountSource()


class Message(zeit.push.message.Message):

    grok.name('facebook')
    get_text_from = 'long_text'


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
    options.redirect_uri = 'http://vivi.zeit.de/@@ping'

    # Step 1: Get user token. <https://developers.facebook.com
    # /docs/facebook-login/manually-build-a-login-flow#login>
    login_url = 'https://www.facebook.com/dialog/oauth?' + urllib.urlencode({
        'client_id': options.app_id,
        'redirect_uri': options.redirect_uri,
        'scope': 'manage_pages,publish_actions',
    })
    print u'Bitte bei Facebook anmelden und dann diese URL öffnen:\n%s' % (
        login_url)
    print (
        u'Nach der Bestätigung der Berechtigungen erfolgt eine Weiterleitung,')
    result_url = raw_input('die neue URL bitte hier eingeben: ')
    code = urlparse.parse_qs(urlparse.urlparse(result_url).query)['code'][0]

    # Step 1b: Convert code to token <https://developers.facebook.com
    # /docs/facebook-login/manually-build-a-login-flow#confirm>
    r = requests.get(
        'https://graph.facebook.com/oauth/access_token?' + urllib.urlencode({
            'client_id': options.app_id,
            'client_secret': options.app_secret,
            'redirect_uri': options.redirect_uri,
            'code': code,
        }))
    result = urlparse.parse_qs(r.text)
    if 'error' in result:
        print result['error']
        raise SystemExit(1)
    short_lived_user_token = result['access_token'][0]

    # Step 2: Exchange for long-lived token. <https://developers.facebook.com
    # /docs/facebook-login/access-tokens/#extending>
    r = requests.get(
        'https://graph.facebook.com/oauth/access_token?' + urllib.urlencode({
            'client_id': options.app_id,
            'client_secret': options.app_secret,
            'grant_type': 'fb_exchange_token',
            'fb_exchange_token': short_lived_user_token,
        }))
    result = urlparse.parse_qs(r.text)
    if 'error' in result:
        print result['error']
        raise SystemExit(1)
    long_lived_user_token = result['access_token'][0]

    # Step 3. Retrieve page access token. <https://developers.facebook.com
    # /docs/facebook-login/access-tokens/#pagetokens>
    #
    # Note: Since we used a long-lived user token, the page token will be
    # long-lived (~60 days), too.
    user = fb.graph.api(long_lived_user_token)
    accounts = user.get_object(cat='single', id='me', fields=['accounts'])
    page_token = [x['access_token'] for x in accounts['accounts']['data']
                  if x['name'] == options.page_name][0]

    print u'Das Page Token für %s ist: %s' % (options.page_name, page_token)
