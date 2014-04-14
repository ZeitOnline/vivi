import logging
import zeit.push.interfaces
import zope.interface


log = logging.getLogger(__name__)

parse_settings = {
    # The ``test`` app
    'application_id': 'qSv7GGSS8Bpxtt9t1GGE61gxIOpyP9oPNziHVpFh',
    'rest_api_key': 'pR4mNy8Q1w8En9PqZtp3xIrvkdvQumrhS7QycA7K',

    # Web UI only
    'username': 'ws+parse@gocept.com',
    'password': 'LidCaf3Jogvo',
}


class PushNotifier(object):

    zope.interface.implements(zeit.push.interfaces.IPushNotifier)

    def __init__(self):
        self.reset()

    def reset(self):
        self.calls = []

    def send(self, text, link, title=None):
        self.calls.append((text, link, title))
        log.info('PushNotifier.send(%s)', dict(
            text=text, link=link, title=title))
