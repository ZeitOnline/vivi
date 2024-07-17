import logging

import requests
import zope.interface

import zeit.cms.config
import zeit.push.interfaces


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
class Connection:
    """Writes an event to Grafana annotations."""

    def __init__(self, base_url, apikey):
        self.base_url = base_url
        self.apikey = apikey

    def send(self, text, link, **kw):
        if not self.base_url:
            return
        template = kw.get('payload_template', '').replace('.json', '')
        log.debug('Sending push to %s: %s', self.base_url, link)
        requests.post(
            self.base_url + '/api/annotations',
            headers={'Authorization': 'Bearer %s' % self.apikey},
            json={'text': link, 'tags': ['push', 'www', template]},
            timeout=2,
        )


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
def from_product_config():
    config = zeit.cms.config.package('zeit.push')
    return Connection(config['grafana-url'], config['grafana-apikey'])
