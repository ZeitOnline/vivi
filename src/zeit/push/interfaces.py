from zeit.cms.i18n import MessageFactory as _
import xml.sax.saxutils
import zc.sourcefactory.source
import zeit.cms.content.sources
import zope.interface
import zope.schema


class IMessage(zope.interface.Interface):

    def send():
        """XXX docme"""


class IPushNotifier(zope.interface.Interface):

    def send(text, link, **kw):
        """Sends the given ``text`` as a push message through an external
        service.

        The ``link`` (an URL) will be integrated into the message (how this
        happens depends on the medium, possibilities include appending to the
        text, attaching as metadata, etc.).

        Additional kw parameters:
        ``title`` is only supported by Parse.com at the moment.
        It can be thought of as the title of the dialog window that displays
        the push message.

        """


class WebServiceError(Exception):
    """A web service was unable to process a request because of semantic
    problems.
    """


class TechnicalError(Exception):
    """A web service had a technical error.
    The request could be retried later on.
    """


class IPushMessages(zope.interface.Interface):
    """Configures which push services should be notified when this
    ICMSContent is published.

    This works as follows: For all properties that are True, look up a named
    IPushNotifier utility of the same name.

    """

    date_last_pushed = zope.schema.Datetime(
        title=_('Last push'), required=False, readonly=True)

    # BBB deprecated, Facebook texts are now stored per account in
    # message_config.
    long_text = zope.schema.Text(
        title=_('Long push text'), required=False)
    short_text = zope.schema.TextLine(
        title=_('Short push text'),
        required=False,
        # 117 + 1 Space + 22 characters t.co-URL = 140
        #
        # XXX It's not yet clear what we can do when the user enters another
        # URL as part of the tweet and that URL gets *longer* during the
        # shortening process.
        max_length=117)

    """A message configuration is a dict with at least the following keys:
       - type: Kind of service (twitter, facebook, ...). Must correspond
         to the utility name of an IPushNotifier.
       - enabled: Boolean. This allows keeping the message configuration even
         when it should not be used at the moment, e.g. for different text to
         different accounts.

    Any other keys are type-dependent. (A common additional key is ``account``,
    e.g. Twitter and Facebook support posting to different accounts.)

    """
    message_config = zope.schema.Tuple(required=False, default=())

    messages = zope.interface.Attribute(
        'List of IMessage objects, one for each enabled message_config entry')


PARSE_NEWS_CHANNEL = 'parse-channel-news'
PARSE_BREAKING_CHANNEL = 'parse-channel-breaking'


class IPushURL(zope.interface.Interface):
    """Adapts ICMSContent to the uniqueId that is used to calculate the URL
    to be transmitted in the push message.

    Usually, that's the uniqueId of the ICMSContent itself, but this interface
    provides an extension point for special treatments of certain content
    types, e.g. zeit.content.link objects.
    """


class TwitterAccountSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.push'
    config_url = 'twitter-accounts'
    attribute = 'name'

    class source_class(zc.sourcefactory.source.FactoredContextualSource):

        @property
        def MAIN_ACCOUNT(self):
            return self.factory.main_account()

    @classmethod
    def main_account(cls):
        config = zope.app.appsetup.product.getProductConfiguration(
            cls.product_configuration)
        return config['twitter-main-account']

    def isAvailable(self, node, context):
        return (super(TwitterAccountSource, self).isAvailable(node, context)
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
        return (node.get('token'), node.get('secret'))

twitterAccountSource = TwitterAccountSource()


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


class IAccountData(zope.interface.Interface):
    """Convenicence acess to IPushMessages.message_config entries"""

    facebook_main_enabled = zope.schema.Bool(title=_('Enable Facebook'))
    facebook_main_text = zope.schema.Text(
        title=_('Facebook Main Text'), required=False)
    facebook_magazin_enabled = zope.schema.Bool(
        title=_('Enable Facebook Magazin'))
    facebook_magazin_text = zope.schema.Text(
        title=_('Facebook Magazin Text'), required=False)
    twitter_main_enabled = zope.schema.Bool(title=_('Enable Twitter'))
    twitter_ressort_enabled = zope.schema.Bool(
        title=_('Enable Twitter Ressort'))
    twitter_ressort = zope.schema.Choice(
        title=_('Additional Twitter'),
        source=twitterAccountSource,
        required=False)
    mobile_text = zope.schema.TextLine(title=_('Mobile title'), required=False)
    mobile_enabled = zope.schema.Bool(title=_('Enable mobile push'))
