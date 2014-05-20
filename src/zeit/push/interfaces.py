import zope.interface


class IPushNotifier(zope.interface.Interface):

    def send(text, link, title=None):
        """Sends the given ``text`` as a push message through an external
        service.

        The ``link`` (an URL) will be integrated into the message (how this
        happens depends on the medium, possibilities include appending to the
        text, attaching as metadata, etc.).

        ``title`` is optional, and at the moment only Parse.com supports it.
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


class IPushServices(zope.interface.Interface):
    """Configures which push services should be notified when this
    ICMSContent is published.

    This works as follows: For all properties that are True, look up a named
    IPushNotifier utility of the same name.

    """

    enabled = zope.schema.Bool(
        title=u'Push?', required=False, default=False, readonly=True)
    date_last_pushed = zope.schema.Datetime(
        title=u'Last push', required=False, readonly=True)

    parse = zope.schema.Bool(title=u'Parse.com', required=False, default=True)
    homepage = zope.schema.Bool(
        title=u'Homepage', required=False, default=True)

PUSH_SERVICES = [x for x in list(IPushServices) if x not in (
    'enabled', 'date_last_pushed')]
