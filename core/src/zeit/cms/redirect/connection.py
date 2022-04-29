from six.moves.urllib.parse import urlparse
import json
import requests
import zeit.cms.redirect.interfaces
import zope.app.appsetup.product
import zope.interface


@zope.interface.implementer(zeit.cms.redirect.interfaces.ILookup)
class Lookup:

    def __init__(self, url):
        self.url = url
        if self.url.endswith('/'):
            self.url = self.url[:-1]

    def rename(self, old_id, new_id):
        parameters = {
            'source': urlparse(old_id).path,
            'target': urlparse(new_id).path,
        }
        response = requests.post(self.url + '/_add',
                                 data=json.dumps(parameters),
                                 headers={'Content-Type': 'application/json'})
        if response.status_code != 200:
            raise self._error(response)

    def find(self, uniqueId):
        parsed = urlparse(uniqueId)
        response = requests.get(self.url + parsed.path,
                                allow_redirects=False,
                                headers={'Host': parsed.netloc})
        if response.status_code == 200:
            return None
        if response.status_code == 301:
            return response.headers['Location']
        raise self._error(response)

    def _error(self, response):
        return RuntimeError('Redirect server returned HTTP %s: %s' % (
            response.status_code, response.text))


@zope.interface.implementer(zeit.cms.redirect.interfaces.ILookup)
def from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
    return Lookup(config['redirect-service-url'])
