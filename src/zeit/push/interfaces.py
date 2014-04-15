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

    parse = zope.schema.Bool(title=u'Parse.com', required=False, default=True)

    # XXX twitter, facebook, homepage, centerpage
