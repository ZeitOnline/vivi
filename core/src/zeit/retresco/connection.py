from zeit.cms.checkout.helper import checked_out
import gocept.runner
import grokcore.component as grok
import logging
import lxml.builder
import pytz
import requests
import requests.exceptions
import requests.sessions
import signal
import urllib
import zeit.cms.interfaces
import zeit.cms.tagging.interfaces
import zeit.cms.workflow.interfaces
import zeit.content.rawxml.interfaces
import zeit.retresco.interfaces
import zeit.retresco.tag
import zope.app.appsetup.product
import zope.component
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

    def extract_keywords(self, content):
        __traceback_info__ = (content.uniqueId,)

        response = self.enrich(content, intextlinks=False)
        return self.generate_keyword_list(response)

    def generate_keyword_list(self, response):
        result = []
        for entity_type in zeit.retresco.interfaces.ENTITY_TYPES:
            for keyword in response.get('rtr_{}s'.format(entity_type), ()):
                result.append(zeit.retresco.tag.Tag(
                    label=keyword, entity_type=entity_type))
        return result

    def get_keywords(self, search_string, entity_type=None):
        __traceback_info__ = (search_string,)
        params = {'q': search_string}
        if entity_type is not None:
            params['item_type'] = entity_type
        response = self._request('GET /entities', params=params)
        for entity in response['entities']:
            yield zeit.retresco.tag.Tag(
                entity['entity_name'], entity['entity_type'])

    def get_locations(self, search_string):
        return self.get_keywords(search_string, entity_type='location')

    def get_all_topicpages(self):
        start = 0
        # XXX figure out row number that balances number of requests vs.
        # work the TMS has to do per request.
        rows = 100
        while True:
            result = self.get_topicpages(start, rows)
            start += rows
            if not result:
                break
            for row in result:
                yield row

    def get_topicpages(self, start=0, rows=25):
        response = self._request(
            'GET /topic-pages',
            params={'q': '*', 'page': int(start / rows) + 1, 'rows': rows})
        result = zeit.cms.interfaces.Result()
        result.hits = response['num_found']
        for row in response['docs']:
            row['id'] = zeit.cms.interfaces.normalize_filename(row['doc_id'])
            result.append(row)
        return result

    def get_topicpage_documents(self, id, start=0, rows=25):
        response = self._request(
            'GET /topic-pages/{}/documents'.format(id),
            params={'page': int(start / rows) + 1, 'rows': rows})
        result = zeit.cms.interfaces.Result()
        result.hits = response['num_found']
        for row in response['docs']:
            page = row['payload']
            page[u'uniqueId'] = (
                zeit.cms.interfaces.ID_NAMESPACE + row['url'][1:])
            page[u'doc_type'] = row['doc_type']
            page[u'doc_id'] = row['doc_id']
            page[u'keywords'] = []
            for entity_type in zeit.retresco.interfaces.ENTITY_TYPES:
                for keyword in row.get('rtr_{}s'.format(entity_type), ()):
                    page[u'keywords'].append(zeit.retresco.tag.Tag(
                        label=keyword, entity_type=entity_type))
            result.append(page)
        return result

    def get_article_body(self, uuid, timeout=None):
        __traceback_info__ = (uuid,)
        try:
            response = self._request(
                'GET /content/{}'.format(urllib.quote(uuid)), timeout=timeout)
            return response['body']
        except (KeyError, requests.Timeout):
            return None

    def index(self, content, override_body=None):
        __traceback_info__ = (content.uniqueId,)
        data = zeit.retresco.interfaces.ITMSRepresentation(content)()

        if data is None:
            log.info('Skip index for %s, it is missing required fields',
                     content.uniqueId)
            return {}
        if override_body is not None:
            data['body'] = override_body

        return self._request('PUT /content/%s' % data['doc_id'], json=data)

    def publish(self, content):
        __traceback_info__ = (content.uniqueId,)
        uuid = zeit.cms.content.interfaces.IUUID(content).id
        return self._request('POST /content/%s/publish' % uuid)

    def enrich(self, content, intextlinks=True):
        __traceback_info__ = (content.uniqueId,)
        data = zeit.retresco.interfaces.ITMSRepresentation(content)()
        if data is None:
            log.info(
                'Skip enrich for %s, it is missing required fields',
                content.uniqueId)
            return {}
        params = {}
        if intextlinks:
            params['in-text-linked'] = ''

        return self._request(
            'POST /enrich', params=params, json=data)

    def delete_id(self, uuid):
        try:
            self._request('DELETE /content/%s' % uuid)
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
            url = self.url + path
            if 'in-text-linked' in kw.get('params', {}).keys():
                url = url + '?in-text-linked'
                kw.pop('params')
            response = method(url, **kw)
            response.raise_for_status()
        except requests.exceptions.RequestException, e:
            status = getattr(e.response, 'status_code', 500)
            body = getattr(e.response, 'text', '<body/>')
            message = '{verb} {path} {error!r}\n{body}'.format(
                verb=verb, path=path, error=e, body=body)
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


@gocept.runner.once(principal=gocept.runner.from_config(
    'zeit.retresco', 'topiclist-principal'))
def update_topiclist():
    _update_topiclist()


def _update_topiclist():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.retresco')
    keywords = zeit.cms.interfaces.ICMSContent(config['topiclist'], None)
    if not zeit.content.rawxml.interfaces.IRawXML.providedBy(keywords):
        raise ValueError(
            '%s is not a raw xml document' % config['topiclist'])
    with checked_out(keywords) as co:
        log.info('Retrieving all topic pages from TMS')
        co.xml = _build_topic_xml()
    zeit.cms.workflow.interfaces.IPublish(keywords).publish(async=False)


def _build_topic_xml():
    tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
    E = lxml.builder.ElementMaker()
    root = E.topics()
    for row in tms.get_all_topicpages():
        # XXX What other attributes might be interesting to use in a
        # dynamicfolder template?
        root.append(E.topic(row['title'], id=row['id']))
    return root


class Topicpages(grok.GlobalUtility):

    zope.interface.implements(zeit.cms.tagging.interfaces.ITopicpages)

    def get_topics(self, start=0, rows=25):
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        return tms.get_topicpages(start, rows)


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


def signal_timeout_request(self, method, url, **kw):
    """The requests library does not allow to specify a duration within which
    a request has to return a response. You can only limit the time to
    wait for the connection to be established or the first byte to be sent.

    We now utilize the SIGALRM signal to enforce a hard timeout and abort the
    request even if the server is still sending its response.
    """

    class SignalTimeout(Exception):
        pass

    def handler(signum, frame):
        raise SignalTimeout()

    try:
        # Handler registration fails if it's attempted in a worker thread
        signal.signal(signal.SIGALRM, handler)
        # Timeout tuples (connect, read) shall not invoke signal timeouts
        sig_timeout = float(kw['timeout'])
    except (KeyError, TypeError, ValueError):
        sig_timeout = None
    else:
        signal.setitimer(signal.ITIMER_REAL, sig_timeout)

    try:
        return original_session_request(self, method, url, **kw)
    except SignalTimeout:
        raise requests.exceptions.Timeout(
            'Request attempt timed out after %s seconds' % sig_timeout)
    finally:
        if sig_timeout:
            signal.setitimer(signal.ITIMER_REAL, 0)

original_session_request = requests.sessions.Session.request
requests.sessions.Session.request = signal_timeout_request
