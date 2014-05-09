import zope.interface


class IPushNotifier(zope.interface.Interface):

    def send(text, link, title=None):
        """XXX docme
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

    # XXX twitter, facebook, homepage, centerpage

PUSH_SERVICES = [x for x in list(IPushServices) if x not in (
    'enabled', 'date_last_pushed')]
