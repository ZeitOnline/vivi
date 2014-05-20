import logging
import zeit.cms.testing
import zeit.content.article.testing
import zeit.push.interfaces
import zeit.workflow.testing
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

    def send(self, text, link, **kw):
        self.calls.append((text, link, kw))
        log.info('PushNotifier.send(%s)', dict(
            text=text, link=link, kw=kw))


ZCML_LAYER = zeit.cms.testing.ZCMLLayer('testing.zcml', product_config=(
    zeit.cms.testing.cms_product_config
    + zeit.workflow.testing.product_config
    + zeit.content.article.testing.product_config))


class TestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZCML_LAYER
