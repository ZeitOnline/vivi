from six import StringIO
from zeit.cms.checkout.helper import checked_out
import collections
import gocept.runner
import logging
import lxml.builder
import requests
import requests.exceptions
import requests.sessions
import signal
import transaction
import zeit.cms.interfaces
import zeit.cms.workflow.interfaces
import zeit.content.rawxml.interfaces
import zeit.retresco.interfaces
import zeit.retresco.tag
import zope.app.appsetup.product
import zope.component
import zope.interface


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.retresco.interfaces.ITMS)
class TMS(object):

    def __init__(self, primary, secondary=None):
        self.primary = dict(primary)
        self.secondary = dict(secondary or {})
        for conn in self.primary, self.secondary:
            url = conn.get('url') or ''
            if url.endswith('/'):
                conn['url'] = url.rstrip('/')

        # Keep internal API stable for zeit.web
        self.url = self.primary['url']

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
            params={'q': '*',
                    'page': int(start / max(rows, 1)) + 1,
                    'rows': rows})
        result = zeit.cms.interfaces.Result()
        result.hits = response['num_found']
        for row in response['docs']:
            row['id'] = zeit.cms.interfaces.normalize_filename(row['doc_id'])
            result.append(row)
        return result

    def get_topicpage_documents(self, id, start=0, rows=25, filter=None):
        params = {'start': start, 'rows': rows}
        if filter is not None:
            params['filter'] = filter
        response = self._request(
            'GET /topic-pages/{}/documents'.format(id),
            params=params)
        result = zeit.cms.interfaces.Result(response['docs'])
        result.hits = response['num_found']
        return result

    def get_related_documents(self, uuid, rows=15, filtername=None):
        params = {'rows': rows}
        url = 'GET /content/{}/relateds'.format(uuid)
        if filter:
            url = url + '?filter={}'.format(filtername)
        response = self._request(url, params=params)
        result = zeit.cms.interfaces.Result(response['docs'])
        result.hits = len(response['docs'])
        return result

    def get_article_data(self, content):
        uuid = zeit.cms.content.interfaces.IUUID(content).id
        try:
            return self._request('GET /content/%s' % uuid)
        except Exception:
            return {}

    def get_article_body(self, content, timeout=None, published=True):
        if published:
            return self._get_intextlink_data(content, timeout).get('body')
        else:
            return self._get_intextlink_data_preview(content,
                                                     timeout).get('body')

    def _get_intextlink_data(self, content, timeout):
        __traceback_info__ = (content.uniqueId,)
        uuid = zeit.cms.content.interfaces.IUUID(content).id
        if uuid is None:
            log.warning('%s has no UUID, intextlinks request skipped', content)
            return {}
        try:
            response = self._request(
                'GET /in-text-linked-documents/%s' % uuid, timeout=timeout)
            return response
        except (KeyError, requests.Timeout):
            return {}

    def _get_intextlink_data_preview(self, content, timeout):
        # In contrast to _get_intextlink_data, the tms computes the
        # the intext_links from the given content, and does not look it up
        tms_content = zeit.retresco.interfaces.ITMSRepresentation(content)()
        if not tms_content:
            return {}
        try:
            return self._request(
                'POST /in-text-linked-documents-preview',
                json=tms_content,
                timeout=timeout)
        except requests.Timeout:
            log.warning(
                '/in-text-linked-documents-preview request for %s timed out',
                content.uniqueId)
            return {}

    def get_article_keywords(self, content, timeout=None, published=True):
        if published:
            response = self._get_intextlink_data(content, timeout)
        else:
            response = self._get_intextlink_data_preview(content, timeout)
        data = response.get('entity_links', ())
        entity_links = collections.OrderedDict()
        for item in data:
            if not item['link']:
                continue
            # zeit.web expects the path without a leading slash
            item['link'] = item['link'].lstrip('/')
            entity_links[(item['key'], item['key_type'])] = item

        # Keywords pinned in vivi come first.
        result = []
        content = zeit.retresco.interfaces.ITMSContent(response)
        for keyword in zeit.retresco.tagger.Tagger(content).values():
            if not keyword.pinned:
                continue
            tms = entity_links.pop((keyword.label, keyword.entity_type), None)
            if not tms:
                continue
            keyword.link = tms['link']
            result.append(keyword)
        # Then we add the rest, TMS returns those sorted by descending score.
        for tms in entity_links.values():
            keyword = zeit.retresco.tag.Tag(tms['key'], tms['key_type'])
            keyword.link = tms['link']
            result.append(keyword)

        return result

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

    def unpublish_id(self, uuid):
        return self._request('POST /content/%s/unpublish' % uuid)

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
        except zeit.retresco.interfaces.TMSError as e:
            if e.status == 404:
                log.debug(
                    'Warning: Tried to delete non-existent %s, ignored.', uuid)
            else:
                raise

    def _request(self, request, **kw):
        result = self._request_one(tms=self.primary, request=request, **kw)
        verb, _, _ = request.partition(' ')
        if verb in {'POST', 'PUT', 'DELETE'} and self.secondary.get('url'):
            self._request_one(tms=self.secondary, request=request, **kw)
        return result

    def _request_one(self, tms, request, **kw):
        verb, path = request.split(' ', 1)
        method = getattr(requests, verb.lower())
        if tms.get('username'):
            kw['auth'] = (tms['username'], tms['password'])
        try:
            url = tms['url'] + path
            if 'in-text-linked' in kw.get('params', {}).keys():
                url = url + '?in-text-linked'
                kw.pop('params')
            response = method(url, **kw)
            log.debug(dump_request(response))
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            status = getattr(e.response, 'status_code', 500)
            body = getattr(e.response, 'text', '(no error detail)')
            message = '{verb} {path} {error!r}\n{body}'.format(
                verb=verb, path=path, error=e, body=body)
            if status < 500:
                raise zeit.retresco.interfaces.TMSError(message, status)
            raise zeit.retresco.interfaces.TechnicalError(message, status)
        try:
            return response.json()
        except ValueError:
            message = '{verb} {path} returned invalid json'.format(
                verb=verb, path=path)
            raise zeit.retresco.interfaces.TechnicalError(message, 590)


@zope.interface.implementer(zeit.retresco.interfaces.ITMS)
def from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.retresco')
    prefix = 'primary-' if 'primary-base-url' in config else ''
    return TMS(
        primary=dict(
            url=config.get('{}base-url'.format(prefix)),
            username=config.get('{}username'.format(prefix)),
            password=config.get('{}password'.format(prefix))),
        secondary=dict(
            url=config.get('secondary-base-url'),
            username=config.get('secondary-username'),
            password=config.get('secondary-password')))


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
    redirects = zeit.cms.interfaces.ICMSContent(
        config['topic-redirect-id'], None)
    if not zeit.content.text.interfaces.IText.providedBy(redirects):
        raise ValueError(
            '%s is not a text document' % config['topic-redirect-id'])

    log.info('Retrieving all topic pages from TMS')
    tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
    topicpages = tms.get_all_topicpages()

    with checked_out(keywords) as co:
        co.xml = _build_topic_xml(topicpages)
    zeit.cms.workflow.interfaces.IPublish(keywords).publish(background=False)
    try:
        transaction.commit()
    except Exception:
        # We don't really care about the DAV cache, to be honest. Worst case we
        # won't see the matching zeit.objectlog entry for this publish.
        transaction.abort()
        log.warning('Error during commit', exc_info=True)

    # Refresh iterator
    topicpages = tms.get_all_topicpages()
    with checked_out(redirects) as co:
        co.text = _build_topic_redirects(topicpages)
    zeit.cms.workflow.interfaces.IPublish(redirects).publish(background=False)


TOPIC_PAGE_ATTRIBUTES = {
    'id': '',
    'topic_type': 'type',
}


def _build_topic_xml(topicpages):
    E = lxml.builder.ElementMaker()
    root = E.topics()
    for row in topicpages:
        if row.get('redirect'):
            continue
        attributes = {}
        for tms, vivi in TOPIC_PAGE_ATTRIBUTES.items():
            if not vivi:
                vivi = tms
            attributes[vivi] = row[tms]
        root.append(E.topic(row['title'], **attributes))
    return root


def _build_topic_redirects(topicpages):
    config = zope.app.appsetup.product.getProductConfiguration('zeit.retresco')
    url_prefix = config['topic-redirect-prefix']

    output = StringIO()
    output.write(
        '# Generated by zeit.retresco.connection.update_topiclist(),'
        ' do not edit.\n\n')

    for row in topicpages:
        target = row.get('redirect')
        if not target:
            continue
        if not target.startswith('http'):
            if not target.startswith('/'):
                target = u'/' + target
            target = url_prefix + target
        # XXX hard-coded path
        source = u'/thema/' + row['id']
        output.write('%s = %s\n' % (source, target))

    return output.getvalue()


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


def dump_request(response):
    """Debug helper. Pass a `requests` response and receive an executable curl
    command line.
    """
    request = response.request
    command = "curl -X {method} -H {headers} -d '{data}' '{uri}'"
    method = request.method
    uri = request.url
    data = request.body
    headers = ["'{0}: {1}'".format(k, v) for k, v in request.headers.items()]
    headers = " -H ".join(headers)
    return command.format(
        method=method, headers=headers, data=data, uri=uri)
