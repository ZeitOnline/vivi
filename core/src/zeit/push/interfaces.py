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
