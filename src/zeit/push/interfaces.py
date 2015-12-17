from zeit.cms.i18n import MessageFactory as _
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
