import zope.interface


class IPushNotifier(zope.interface.Interface):

    def send(title, body, link):
        """XXX docme
        """


class WebServiceError(Exception):
    """A web service was unable to process a request because of semantic
    problems.
    """
