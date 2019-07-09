from StringIO import StringIO
import lxml.etree
import pkg_resources
import requests
import zeit.content.image.interfaces
import zope.interface


USER_AGENT = 'zeit.content.image/' + pkg_resources.get_distribution(
    'vivi.core').version


class MDB(object):

    zope.interface.implements(zeit.content.image.interfaces.IMDB)

    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password

    def get_metadata(self, mdb_id):
        response = self._request('GET /mdb/%s' % mdb_id)
        data = lxml.etree.fromstring(response.text)
        filename = data.xpath('//filename')
        filename = filename[0].text if filename else 'master.jpg'
        result = {
            'mdb_id': mdb_id,
            'filename': filename,
        }
        nodes = (data.xpath('//mediadata_content[@type="text"]') +
                 data.xpath('//mdb_content[@type="text"]'))
        for node in nodes:
            value = node.find('data')
            if value is None:
                continue
            value = value.text.strip() if value.text else None
            if not value:
                continue
            result[node.get('placeholder_name')] = value
        return result

    def get_body(self, mdb_id):
        return StringIO()

    def _request(self, request, **kw):
        verb, path = request.split(' ')
        method = getattr(requests, verb.lower())
        headers = kw.setdefault('headers', {})
        headers['IR-USERNAME'] = self.username
        headers['IR-PASSWORD'] = self.password
        headers['User-Agent'] = USER_AGENT
        response = method(self.url + path, **kw)
        response.raise_for_status()
        return response


@zope.interface.implementer(zeit.content.image.interfaces.IMDB)
def from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.content.image')
    return MDB(
        config['mdb-api-url'],
        config['mdb-api-username'],
        config['mdb-api-password'])
