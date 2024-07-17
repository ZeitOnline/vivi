from io import BytesIO
import base64
import importlib.metadata
import os.path
import re

import lxml.etree
import pendulum
import requests
import zope.interface

import zeit.cms.config
import zeit.content.image.interfaces


USER_AGENT = 'zeit.content.image/' + importlib.metadata.version('vivi.core')
XML_TAGS = re.compile('</?[^>]*>')
FILE_NAME_ATTRIBUTE = re.compile(' name="([^"]*)"')


@zope.interface.implementer(zeit.content.image.interfaces.IMDB)
class MDB:
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password

    def get_metadata(self, mdb_id):
        response = self._request('GET /mdb/%s' % mdb_id)
        data = lxml.etree.fromstring(response.text)

        filename = data.xpath('//filename')
        filename = filename[0].text if filename else 'master.jpg'
        expires = data.xpath('//expiration_date')
        expires = expires[0].text if expires else None
        if expires and expires != '0000-00-00':
            expires = pendulum.parse(expires, tz='Europe/Berlin').isoformat()
        else:
            expires = None

        result = {
            'mdb_id': mdb_id,
            'filename': filename,
            'expires': expires,
        }

        nodes = data.xpath('//mediadata_content[@type="text"]') + data.xpath(
            '//mdb_content[@type="text"]'
        )
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
        response = self._request('GET /mdb/%s/file' % mdb_id)
        response = response.text
        # Yep, they're sending megabytes of data in an XML envelope; let's not
        # put that through an XML parser without a really good reason.
        body = XML_TAGS.sub('', response)
        body = base64.b64decode(body)
        result = BytesIO(body)
        result.filename = FILE_NAME_ATTRIBUTE.search(response).group(1)
        result.mdb_id = mdb_id
        result.headers = {'content-type': 'image/%s' % os.path.splitext(result.filename)[1].lower()}
        return result

    def _request(self, request, **kw):
        verb, path = request.split(' ')
        method = getattr(requests, verb.lower())
        headers = kw.setdefault('headers', {})
        headers['IR-USERNAME'] = self.username
        headers['IR-PASSWORD'] = self.password
        headers['User-Agent'] = USER_AGENT
        response = method(self.url + path, **kw)
        response.raise_for_status()
        # XXX IR does not declare the charset, but apparently it's utf-8.
        response.encoding = 'utf-8'
        return response


class FakeMDB(MDB):
    def __init__(self, *args):
        pass

    def _request(self, request, **kw):
        import requests_mock  # test-only dependency

        if request.endswith('file'):
            filename = 'mdb-body.xml'
        else:
            filename = 'mdb-meta.xml'
        return requests_mock.create_response(
            requests.Request(url='http://example.invalid'),
            content=(
                importlib.resources.files(__package__) / 'tests/fixtures' / filename
            ).read_bytes(),
        )


@zope.interface.implementer(zeit.content.image.interfaces.IMDB)
def from_product_config():
    config = zeit.cms.config.package('zeit.content.image')
    return MDB(config['mdb-api-url'], config['mdb-api-username'], config['mdb-api-password'])
