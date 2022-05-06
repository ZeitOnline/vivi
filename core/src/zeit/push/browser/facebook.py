from zeit.cms.i18n import MessageFactory as _
import fb
import gocept.form.grouped
import requests
import urllib.parse
import zeit.cms.browser.menu
import zope.app.appsetup.product
import zope.formlib.form
import zope.session.interfaces


class IFacebookApp(zope.interface.Interface):

    app_id = zope.schema.TextLine(
        title=_('Facebook app id'))
    app_secret = zope.schema.TextLine(
        title=_('Facebook app secret'))
    page_name = zope.schema.TextLine(
        title=_('Facebook page name (e.g. "ZEIT ONLINE")'))


class TokenForm(zeit.cms.browser.form.FormBase,
                gocept.form.grouped.Form):

    form_fields = zope.formlib.form.FormFields(IFacebookApp)
    field_groups = (gocept.form.grouped.RemainingFields(_('')),)

    @zope.formlib.form.action(
        _('Create'), condition=zope.formlib.form.haveInputWidgets)
    def redirect_to_facebook(self, action, data):
        data['redirect_uri'] = self.url(
            self.context, 'generate-facebook-token')
        session = zope.session.interfaces.ISession(self.request)
        session['zeit.push.facebook'].update(data)

        # Step 1: Get user token. <https://developers.facebook.com
        # /docs/facebook-login/manually-build-a-login-flow#login>
        scopes = ','.join([
            'pages_read_engagement',
            'pages_manage_posts',
            'business_management',
            'pages_manage_metadata',
            'pages_show_list'
        ])
        url = ('https://www.facebook.com/dialog/oauth?' +
               urllib.parse.urlencode({
                   'client_id': data['app_id'],
                   'redirect_uri': data['redirect_uri'],
                   'scope': scopes,
               }))
        self.request.response.redirect(url, trusted=True)


class GenerateToken(zeit.cms.browser.view.Base):

    def __call__(self):
        code = self.request.form.get('code')
        if not code:
            raise ValueError('Query parameter `code` is missing.')

        # Step 1b: Convert code to token <https://developers.facebook.com
        # /docs/facebook-login/manually-build-a-login-flow#confirm>
        r = requests.get(
            'https://graph.facebook.com/oauth/access_token?' +
            urllib.parse.urlencode({
                'client_id': self.settings['app_id'],
                'client_secret': self.settings['app_secret'],
                'redirect_uri': self.settings['redirect_uri'],
                'code': code,
            }))
        if 'error' in r.text:
            raise ValueError(r.text)
        short_lived_user_token = r.json()['access_token']

        # Step 2: Exchange for long-lived token.
        # <https://developers.facebook.com
        # /docs/facebook-login/access-tokens/#extending>
        r = requests.get(
            'https://graph.facebook.com/oauth/access_token?' +
            urllib.parse.urlencode({
                'client_id': self.settings['app_id'],
                'client_secret': self.settings['app_secret'],
                'grant_type': 'fb_exchange_token',
                'fb_exchange_token': short_lived_user_token,
            }))
        if 'error' in r.text:
            raise ValueError(r.text)
        long_lived_user_token = r.json()['access_token']

        # Step 3. Retrieve page access token. <https://developers.facebook.com
        # /docs/facebook-login/access-tokens/#pagetokens>
        #
        # Note: Since we used a long-lived user token, the page token will be
        # long-lived (~60 days), too.
        user = fb.graph.api(long_lived_user_token)
        accounts = user.get_object(cat='single', id='me', fields=['accounts'])
        self.page_token = [
            x['access_token'] for x in accounts['accounts']['data']
            if x['name'] == self.settings['page_name']][0]

        return super().__call__()

    @property
    def settings(self):
        session = zope.session.interfaces.ISession(self.request)
        return session['zeit.push.facebook']

    @property
    def config_file(self):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.push')
        return config['facebook-accounts']


class MenuItem(zeit.cms.browser.menu.GlobalMenuItem):

    title = _("Facebook Tokens")
    viewURL = '@@facebook-token.html'
    pathitem = '@@facebook-token.html'
