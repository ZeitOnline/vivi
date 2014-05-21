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

    enabled = zope.schema.Bool(
        title=_('Push after next publish?'),
        required=False, default=False)
    date_last_pushed = zope.schema.Datetime(
        title=_('Last push'), required=False, readonly=True)

    long_text = zope.schema.Text(
        title=_('Long push text'), required=False)
    short_text= zope.schema.TextLine(
        title=_('Short push text'), required=False, max_length=120)

    message = zope.interface.Attribute('List of IMessage objects')
    message_config = zope.schema.Tuple(required=False, default=())
