from zeit.cms.tagging.tag import Tag
import logging
import pytz
import requests
import requests.exceptions
import zeit.cms.interfaces
import zeit.retresco.interfaces
import zope.interface


log = logging.getLogger(__name__)


class TMS(object):

    zope.interface.implements(zeit.retresco.interfaces.ITMS)

    def __init__(self, url, username=None, password=None):
        self.url = url
        if self.url.endswith('/'):
            self.url = self.url[:-1]
        self.username = username
        self.password = password

    def get_keywords(self, content):
        __traceback_info__ = (content.uniqueId,)
        data = zeit.retresco.interfaces.ITMSRepresentation(content)()
        if data is None:
            return []
        response = self._request(
            'PUT /documents/%s' % data['doc_id'], params={'enrich': 'true'},
            json=data)
        result = []
        for entity_type in zeit.retresco.interfaces.ENTITY_TYPES:
            for keyword in response.get('rtr_{}s'.format(entity_type), ()):
                result.append(Tag(
                    # Having an ASCII-only ID makes handling easier.
                    code='%s-%s' % (
                        entity_type, keyword.encode('unicode_escape')),
                    label=keyword,
                    url_value=zeit.cms.interfaces.normalize_filename(keyword),
                    entity_type=entity_type
                ))
        return result

    def get_all_topicpages(self):
        page = 0
        while True:
            page += 1
            # XXX figure out row number that balances number of requests vs.
            # work the TMS has to do per request.
            response = self._request(
                'GET /topic-pages',
                params={'q': '*', 'rows': 100, 'page': page})
            if not response['docs']:
                break
            for row in response['docs']:
                yield row

    def get_topicpage_documents(self, id, start=0, rows=25):
        response = self._request(
            'GET /topic-pages/{}/documents'.format(id),
            params={'page': int(start / rows) + 1, 'rows': rows})
        result = Result()
        result.hits = response['num_found']
        for row in response['docs']:
            page = row['payload']
            page[u'uniqueId'] = (
                zeit.cms.interfaces.ID_NAMESPACE + row['url'][1:])
            page[u'doc_type'] = row['doc_type']
            page[u'doc_id'] = row['doc_id']
            for entity_type in zeit.retresco.interfaces.ENTITY_TYPES:
                key = u'rtr_{}s'.format(entity_type)
                if key in row:
                    page[key] = row[key]
            result.append(page)
        return result

    def index(self, content):
        __traceback_info__ = (content.uniqueId,)
        data = zeit.retresco.interfaces.ITMSRepresentation(content)()
        if data is None:
            log.info(
                'Skip indexing %s, it is missing required fields',
                content.uniqueId)
            return
        self._request('PUT /documents/%s' % data['doc_id'], params={
            'index': 'true', 'enrich': 'false'}, json=data)

    def delete_id(self, uuid):
        try:
            self._request('DELETE /documents/%s' % uuid)
        except zeit.retresco.interfaces.TMSError, e:
            if e.status == 404:
                log.debug(
                    'Warning: Tried to delete non-existent %s, ignored.', uuid)
            else:
                raise

    def _request(self, request, **kw):
        verb, path = request.split(' ', 1)
        method = getattr(requests, verb.lower())
        if self.username:
            kw['auth'] = (self.username, self.password)
        if 'json' in kw:
            kw['json'] = encode_json(kw['json'])
        try:
            response = method(self.url + path, **kw)
            response.raise_for_status()
        except requests.exceptions.RequestException, e:
            status = getattr(e.response, 'status_code', 500)
            message = '{verb} {path} returned {error}\n{body}'.format(
                verb=verb, path=path, error=str(e), body=e.response.text)
            if status < 500:
                raise zeit.retresco.interfaces.TMSError(message, status)
            raise zeit.retresco.interfaces.TechnicalError(message)
        try:
            return response.json()
        except ValueError:
            message = '{verb} {path} returned invalid json'.format(
                verb=verb, path=path)
            raise zeit.retresco.interfaces.TechnicalError(message)


@zope.interface.implementer(zeit.retresco.interfaces.ITMS)
def from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.retresco')
    return TMS(
        config['base-url'], config.get('username'), config.get('password'))


class Result(list):

    hits = 0


class JSONTypeConverter(object):
    """Since `requests` does not allow plugging in a different JSON encoder,
    we perform custom type conversion on the python structure _before_ we pass
    it to `requests`.
    """

    def __call__(self, o):
        encoder = getattr(self, type(o).__name__, None)
        if encoder is None:  # Optimize common case: no extra function call.
            return o
        return encoder(o)

    def datetime(self, o):
        return o.astimezone(pytz.UTC).strftime('%Y-%m-%dT%H:%M:%SZ')

    date = datetime

    def dict(self, o):
        return {key: self(value) for key, value in o.items()}

    def list(self, o):
        return [self(x) for x in o]

encode_json = JSONTypeConverter()
