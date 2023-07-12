from io import StringIO
from zeit.cms.checkout.helper import checked_out
import collections
import logging
import lxml.builder
import requests
import requests.exceptions
import requests.sessions
import transaction
import zeit.cms.cli
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.requests
import zeit.cms.tagging.tag
import zeit.cms.workflow.interfaces
import zeit.content.rawxml.interfaces
import zeit.retresco.interfaces
import zope.app.appsetup.product
import zope.component
import zope.interface


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.retresco.interfaces.ITMS)
class TMS:

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
                result.append(zeit.cms.tagging.tag.Tag(
                    label=keyword, entity_type=entity_type))
        return result

    def get_keywords(self, search_string, entity_type=None):
        __traceback_info__ = (search_string,)
        params = {'q': search_string}
        if entity_type is not None:
            params['item_type'] = entity_type
        response = self._request('GET /entities', params=params)
        for entity in response['entities']:
            yield zeit.cms.tagging.tag.Tag(
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

    def get_topicpage_documents(
            self, id, start=0, rows=25, filter=None, order=None):
        params = {'start': start, 'rows': rows}
        if filter is not None:
            params['filter'] = filter
        if order is not None:
            params['sort_by'] = order
        response = self._request(
            'GET /topic-pages/{}/documents'.format(id),
            params=params)
        result = zeit.cms.interfaces.Result(response['docs'])
        result.hits = response['num_found']
        return result

    def get_related_documents(self, content, rows=15, filter=None):
        uuid = zeit.cms.content.interfaces.IUUID(content).id
        params = {'rows': rows}
        if filter:
            params['filter'] = filter

        response = self._request(
            'GET /content/{}/relateds'.format(uuid), params=params)
        result = zeit.cms.interfaces.Result(response['docs'])
        result.hits = len(response['docs'])
        return result

    def _get_related_topicpages(
            self, topicpage_id, rows=10, suppress_errors=False, timeout=None):
        try:
            params = {'rows': rows}
            response = self._request(
                'GET /topic-pages/{}/relateds'.format(topicpage_id),
                params=params, timeout=timeout)
            return response['docs']
        except Exception:
            if not suppress_errors:
                log.warning(
                    'Retresco topiclinks failed for {}'.format(
                        topicpage_id), exc_info=True)
            return ()

    def get_related_topics(self, topicpage_id, rows=10, suppress_errors=False):
        response = self._get_related_topicpages(
            topicpage_id, rows, suppress_errors)
        id_namespace = zeit.cms.interfaces.ID_NAMESPACE.rstrip('/')
        result = zeit.cms.interfaces.Result(
            [id_namespace + x['url'] for x in response])
        result.hits = len(response)
        return result

    def get_content_related_topicpages(
            self, content, rows=10, suppress_errors=False, timeout=None):
        is_metadata = zeit.cms.content.interfaces.ICommonMetadata.providedBy(
            content)
        if not is_metadata or not content.keywords:
            return []

        response = self._get_related_topicpages(
            content.keywords[0].label.lower(), rows, suppress_errors, timeout)
        return get_tagslist(response)

    def _get_content_topics(self, content, timeout=None):
        uuid = zeit.cms.content.interfaces.IUUID(content).id
        response = self._request(
            'GET /content/{}/topic-pages'.format(uuid), timeout=timeout)
        result = zeit.cms.interfaces.Result(response['docs'])
        result.hits = len(response['docs'])
        return result

    def get_content_containing_topicpages(
            self, content, timeout=None, suppress_errors=False):
        try:
            response = self._get_content_topics(content, timeout)
            return get_tagslist(response)
        except Exception:
            if not suppress_errors:
                log.warning(
                    'Retresco topiclinks failed for {}'.format(
                        content.uniqueId), exc_info=True)
            return ()

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

    def get_article_topiclinks(
            self,
            content,
            timeout=None,
            published=True,
            suppress_errors=False):
        try:
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
                tms = entity_links.pop(
                    (keyword.label, keyword.entity_type), None)
                if not tms:
                    continue
                keyword.link = tms['link']
                result.append(keyword)
            # Then we add the rest, TMS returns those sorted by descending
            # score.
            for tms in entity_links.values():
                keyword = zeit.cms.tagging.tag.Tag(
                    tms['key'],
                    tms['key_type'],
                    tms['link'])
                result.append(keyword)
            return result
        except Exception:
            if not suppress_errors:
                log.warning(
                    'Retresco topiclinks failed for {}'.format(
                        content.uniqueId), exc_info=True)
            return ()

    def index(self, content, overrides=None):
        __traceback_info__ = (content.uniqueId,)
        data = zeit.retresco.interfaces.ITMSRepresentation(content)()

        if data is None:
            log.info('Skip index for %s, it is missing required fields',
                     content.uniqueId)
            return {}
        if overrides:
            for key, value in overrides.items():
                data[key] = value

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
            log.debug(zeit.cms.requests.dump_request(response))
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            status = getattr(e.response, 'status_code', 599)
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


@zeit.cms.cli.runner(principal=zeit.cms.cli.from_config(
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


TOPIC_PAGE_ATTRIBUTES = [
    ('id',),
    ('topic_type', 'type'),
]
for i in range(1, 31):
    TOPIC_PAGE_ATTRIBUTES.append(('kpi_%s' % i, None, int))


def _build_topic_xml(topicpages):
    E = lxml.builder.ElementMaker()
    root = E.topics()
    for row in topicpages:
        if row.get('redirect'):
            continue
        attributes = {}
        for attr in TOPIC_PAGE_ATTRIBUTES:
            if len(attr) == 1:
                vivi = tms = attr[0]
            elif len(attr) == 2:
                tms, vivi = attr
            elif len(attr) == 3:
                tms, vivi, _ = attr
                if not vivi:
                    vivi = tms
            value = row.get(tms)
            if value is None:
                continue
            attributes[vivi] = str(value)
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
                target = '/' + target
            target = url_prefix + target
        # XXX hard-coded path
        source = '/thema/' + row['id']
        output.write('%s = %s\n' % (source, target))

    return output.getvalue()


def get_tagslist(response):
    result = []
    for value in response:
        keyword = zeit.cms.tagging.tag.Tag(
            value['name'],
            value['topic_type'],
            value['url'].lstrip('/'))
        result.append(keyword)
    return result
