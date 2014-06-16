import fb
import grokcore.component as grok
import xml.sax.saxutils
import zc.sourcefactory.source
import zeit.push.interfaces
import zeit.push.message
import zope.interface


class Connection(object):

    zope.interface.implements(zeit.push.interfaces.IPushNotifier)

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def send(self, text, link, **kw):
        account = kw['account']
        access_token = facebookAccountSource.factory.access_token(account)

        fb_api = fb.graph.api(access_token)
        message = u'%s %s' % (text, link)
        try:
            fb_api.publish(cat='feed', id='me', message=message)
        except Exception, e:
            raise zeit.push.interfaces.TechnicalError(str(e))


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
def from_product_config():
    # soft dependency
    import zope.app.appsetup.product
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.push')
    return Connection(config['facebook-application-id'],
                      config['facebook-application-secret'])


class FacebookAccountSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.push'
    config_url = 'facebook-accounts'
    attribute = 'name'

    class source_class(zc.sourcefactory.source.FactoredContextualSource):

        @property
        def MAIN_ACCOUNT(self):
            return self.factory.main_account()

    @classmethod
    def main_account(cls):
        config = zope.app.appsetup.product.getProductConfiguration(
            cls.product_configuration)
        return config['facebook-main-account']

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
