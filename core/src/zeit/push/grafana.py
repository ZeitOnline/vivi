import requests
import zeit.push.interfaces
import zope.interface


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
class Connection:
    """Writes an event to Grafana annotations."""

    def __init__(self, base_url, apikey):
        self.base_url = base_url
        self.apikey = apikey

    def send(self, text, link, **kw):
        template = kw.get('payload_template', '').replace('.json', '')
        requests.post(
            self.base_url + '/api/annotations',
            headers={'Authorization': 'Bearer %s' % self.apikey},
            json={'text': link, 'tags': ['push', 'www', template]},
            timeout=2)


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
def from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.push')
    return Connection(config['grafana-url'], config['grafana-apikey'])
