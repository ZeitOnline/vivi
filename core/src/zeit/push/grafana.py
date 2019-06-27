import logging
import requests
import zeit.push.interfaces
import zope.interface


log = logging.getLogger(__name__)


class Connection(object):
    """Writes an event to Grafana annotations."""

    zope.interface.implements(zeit.push.interfaces.IPushNotifier)

    def __init__(self, base_url, apikey):
        self.base_url = base_url
        self.apikey = apikey

    def send(self, text, link, **kw):
        template = kw.get('payload_template', '').replace('.json', '')
        try:
            requests.post(
                self.base_url + '/api/annotations',
                headers={'Authorization': 'Bearer %s' % self.apikey},
                json={'text': link, 'tags': ['push', 'www', template]},
                timeout=2)
        except Exception:
            log.warning(
                'Writing push for %s to grafana failed.', link, exc_info=True)


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
def from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.push')
    return Connection(config['grafana-url'], config['grafana-apikey'])
