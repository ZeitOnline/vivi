from zeit.cms.content.cache import content_cache
from zeit.cms.content.contentuuid import ContentUUID
from zeit.contentquery.helper import QueryHelper
from zope.cachedescriptors.property import Lazy as cachedproperty
import grokcore.component as grok
import json
import logging
import lxml
import requests
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.article.edit.interfaces
import zeit.content.cp.blocks.rss
import zeit.content.cp.blocks.teaser
import zeit.content.cp.interfaces
import zeit.retresco.content
import zeit.retresco.interfaces
import zope.component
import zope.interface


log = logging.getLogger(__name__)


@grok.implementer(zeit.contentquery.interfaces.IContentQuery)
class ContentQuery(grok.Adapter):

    grok.context(zeit.contentquery.interfaces.IConfiguration)
    grok.baseclass()

    total_hits = NotImplemented

    def __call__(self):
        raise NotImplementedError()

    @property
    def start(self):
        """Offset the result by this many content objects"""
        return self.context.start

    @property
    def rows(self):
        """Number of content objects per page"""
        return self.context.count


class ManualLegacyResult(ContentQuery):
    """This is not a automatic content query.
    This returns old style topicboxes with 3 manual references.
    If the  first reference is a centerpage, the ContentQuery object is passed
    to CenterpageContentQuery"""

    grok.name('manual')

    def __call__(self):
        if self.context.referenced_cp:
            return CenterpageContentQuery(self.context)()
        else:
            references = [
                self.context.first_reference,
                self.context.second_reference,
                self.context.third_reference]
            return [ref for ref in references if ref]


class ElasticsearchContentQuery(ContentQuery):
    """Search via Elasticsearch."""

    grok.name('elasticsearch-query')

    include_payload = False  # Extension point for zeit.web and its LazyProxy.

    def __init__(self, context):
        super(ElasticsearchContentQuery, self).__init__(context)
        self.query = json.loads(self.context.elasticsearch_raw_query or '{}')
        self.order = self.context.elasticsearch_raw_order

    def __call__(self):
        self.total_hits = 0
        result = []

        try:
            query = self._build_query()
        except Exception:
            log.warning(
                'Error compiling elasticsearch query %r for %s',
                self.query, self.context.uniqueId, exc_info=True)
            return result

        es = zope.component.getUtility(zeit.retresco.interfaces.IElasticsearch)
        try:
            response = es.search(
                query, self.order,
                start=self.start, rows=self.rows,
                include_payload=self.include_payload)
        except Exception as e:
            log.warning(
                'Error during elasticsearch query %r for %s',
                self.query, self.context.uniqueId, exc_info=True)
            if 'Result window is too large' in str(e):
                # We have to determine the actually available number of hits.
                response = es.search(
                    query, self.order, start=0, rows=0,
                    include_payload=self.include_payload)
            else:
                response = zeit.cms.interfaces.Result()

        self.total_hits = response.hits
        for item in response:
            content = self._resolve(item)
            if content is not None:
                result.append(content)
        return result

    def _build_query(self):
        if self.context.is_complete_query:
            query = self.query
            if self.hide_dupes_clause:
                query = {'query': {'bool': {
                    'must': query,
                    'must_not': self.hide_dupes_clause}}}
        else:
            _query = self.query.get('query', {})
            if not isinstance(_query, list):
                _query = [_query]
            query = {'query': {'bool': {
                'filter': _query + self._additional_clauses,
                'must_not': self._additional_not_clauses[:]}}}
            if self.hide_dupes_clause:
                query['query']['bool']['must_not'].append(
                    self.hide_dupes_clause)
        return query

    _additional_clauses = [
        {'term': {'payload.workflow.published': True}}
    ]

    _additional_not_clauses = [
        {'term': {'payload.zeit__DOT__content__DOT__gallery.type': 'inline'}}
    ]

    def _resolve(self, doc):
        return zeit.cms.interfaces.ICMSContent(
            zeit.cms.interfaces.ID_NAMESPACE[:-1] + doc['url'], None)

    @cachedproperty
    def hide_dupes_clause(self):
        """Perform de-duplication of results.

        Create an id query for teasers that already exist on the CP.
        """
        if not self.context.hide_dupes or not self.context.existing_teasers:
            return None
        ids = []
        for content in self.context.existing_teasers:
            id = getattr(zeit.cms.content.interfaces.IUUID(content, None),
                         'id', None)
            if id:
                ids.append(id)
        if not ids:
            return None
        return {'ids': {'values': ids}}


class CustomContentQuery(ElasticsearchContentQuery):

    grok.name('custom')

    SOLR_TO_ES_SORT = {
        'date-last-published-semantic desc': (
            'payload.workflow.date_last_published_semantic:desc'),
        'last-semantic-change desc': (
            'payload.document.last-semantic-change:desc'),
        'date-first-released desc': (
            'payload.document.date_first_released:desc'),
    }

    ES_FIELD_NAMES = {
        'authorships': 'payload.head.authors',
        'channels': 'payload.document.channels.hierarchy',
        'content_type': 'doc_type',
    }

    def __init__(self, context):
        # Skip direct superclass, as we set `query` and `order` differently.
        super(ElasticsearchContentQuery, self).__init__(context)
        self.queryhelper = QueryHelper()
        self.query = self._make_custom_query()
        self.order = self.context.query_order
        if self.order in self.SOLR_TO_ES_SORT:  # BBB
            self.order = self.SOLR_TO_ES_SORT[self.order]

    def _make_custom_query(self):
        fields = {}
        for item in self.context.query:
            typ = item[0]
            fields.setdefault(typ, []).append(item)

        must = []
        must_not = []
        for typ in sorted(fields):  # Provide stable sorting for tests
            positive = []
            for item in fields[typ]:
                if item[1] == 'neq':
                    must_not.append(self._make_clause(typ, item))
                else:
                    positive.append(item)
            if len(positive) > 1:
                must.append({'bool': {'should': [
                    self._make_clause(typ, x) for x in positive]}})
            elif len(positive) == 1:
                must.append(self._make_clause(typ, positive[0]))
        # We rely on _build_query() putting this inside a bool/filter context
        query = {'query': {'bool': {}}}
        if must:
            query['query']['bool']['filter'] = must
        if must_not:
            query['query']['bool']['must_not'] = must_not
        return query

    def _make_clause(self, typ, item):
        try:
            func = getattr(self, '_make_{}_condition'.format(typ))
            return func(item)
        except AttributeError:
            return self._make_condition(item)

    def _make_condition(self, item):
        typ, operator, value = self.queryhelper._serialize_query_item(
            self.context, item)
        fieldname = self.ES_FIELD_NAMES.get(typ)
        if not fieldname:
            fieldname = self._fieldname_from_property(typ)
        return {'term': {fieldname: value}}

    def _fieldname_from_property(self, typ):
        # XXX Generalize the class?
        prop = getattr(zeit.content.article.article.Article, typ)
        if not isinstance(prop, zeit.cms.content.dav.DAVProperty):
            raise ValueError('Cannot determine field name for %s', typ)
        return 'payload.%s.%s' % (
            zeit.retresco.content.davproperty_to_es(
                prop.namespace, prop.name))

    def _make_ressort_condition(self, item):
        if item[3]:
            return {'bool': {'must': [
                {'term': {
                    self._fieldname_from_property('ressort'): item[2]}},
                {'term': {
                    self._fieldname_from_property('sub_ressort'): item[3]}},
            ]}}
        else:
            return {'term': {
                self._fieldname_from_property('ressort'): item[2]}}


class TMSContentQuery(ContentQuery):

    grok.name('topicpage')
    grok.baseclass()

    def __init__(self, context):
        super(TMSContentQuery, self).__init__(context)
        self.topicpage = self.context.referenced_topicpage
        self.filter_id = self.context.topicpage_filter

    def __call__(self):
        result, _ = self._fetch(self.start)
        return result

    _teaser_count = NotImplemented

    def _fetch(self, start):
        """Extension point for zeit.web to do pagination and de-duping."""

        cache = content_cache(self.context.__parent__, 'topic_queries')
        rows = self._teaser_count + 5  # total teasers + some spares
        key = (self.topicpage, self.filter_id, start)
        if key in cache:
            response, start, _ = cache[key]
        else:
            response, hits = self._get_documents(start=start, rows=rows)
            cache[key] = response, start, hits

        result = []
        dupes = 0
        while len(result) < self.rows:
            try:
                item = next(response)
            except StopIteration:
                start = start + rows            # fetch next batch
                response, hits = self._get_documents(start=start, rows=rows)
                cache[key] = response, start, hits
                try:
                    item = next(response)
                except StopIteration:
                    break                       # results are exhausted

            content = self._resolve(item)
            if content is None:
                continue
            if (self.context.hide_dupes
                    and content in self.context.existing_teasers):
                dupes += 1
            else:
                result.append(content)

        return result, dupes

    def _get_documents(self, **kw):
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        try:
            response = tms.get_topicpage_documents(
                id=self.topicpage, filter=self.filter_id, **kw)
        except Exception as e:
            log.warning('Error during TMS query %r for %s',
                        self.topicpage, self.context.uniqueId, exc_info=True)
            if 'Result window is too large' in str(e):
                # We have to determine the actually available number of hits.
                kw['start'] = 0
                kw['rows'] = 0
                return self._get_documents(**kw)
            return iter([]), 0
        else:
            return iter(response), response.hits

    def _resolve(self, doc):
        return zeit.cms.interfaces.ICMSContent(
            zeit.cms.interfaces.ID_NAMESPACE[:-1] + doc['url'], None)

    @property
    def total_hits(self):
        cache = content_cache(
            self.context.__parent__, 'tms_topic_queries')
        key = (self.topicpage, self.filter_id, self.start)
        if key in cache:
            _, _, hits = cache[key]
        else:
            _, hits = self._get_documents(start=self.start, rows=0)
        return hits


class CPTMSContentQuery(TMSContentQuery):

    grok.context(zeit.content.cp.interfaces.IArea)

    @property
    def _teaser_count(self):
        cp = zeit.content.cp.interfaces.ICenterPage(self.context)
        return sum(
            a.count for a in cp.cached_areas
            if a.automatic and a.count and a.automatic_type == 'topicpage' and
            a.referenced_topicpage == self.topicpage)


class ArticleTMSContentQuery(TMSContentQuery):

    grok.context(zeit.content.article.edit.interfaces.ITopicbox)

    @property
    def _teaser_count(self):
        return self.context.count


class CenterpageContentQuery(ContentQuery):

    grok.name('centerpage')
    # XXX If zeit.web wanted to implement pagination for CP queries, we'd have
    # to walk over the *whole* referenced CP to compute total_hits, which could
    # be rather expensive.

    def __call__(self):
        teasered = zeit.content.cp.interfaces.ITeaseredContent(
            self.context.referenced_cp, iter([]))
        result = []
        for content in teasered:
            if zeit.content.cp.blocks.rss.IRSSLink.providedBy(content):
                continue
            if (self.context.hide_dupes
                    and content in self.context.existing_teasers):
                continue
            result.append(content)
            if len(result) >= self.rows:
                break
        return result


class RSSFeedContentQuery(ContentQuery):

    grok.name('rss-feed')

    def __call__(self):
        self.total_hits = 0
        feed_data = self._parse_feed()
        self.total_hits = len(feed_data)
        return feed_data

    @property
    def rss_feed(self):
        return self.context.rss_feed

    def _parse_feed(self):
        if not self.rss_feed:
            return []
        items = []
        try:
            content = self._get_feed(self.rss_feed.url,
                                     self.rss_feed.timeout)
            xml = lxml.etree.fromstring(content)
        except (requests.exceptions.RequestException,
                lxml.etree.XMLSyntaxError) as e:
            log.debug('Could not fetch feed {}: {}'.format(
                self.rss_feed.url, e))
            return []
        for item in xml.xpath('/rss/channel/item'):
            link = zeit.content.cp.blocks.rss.RSSLink(item, self.rss_feed)
            items.append(link)
        return items

    def _get_feed(self, url, timeout):
        return requests.get(url, timeout=timeout).content


class TMSRelatedApiQuery(TMSContentQuery):

    grok.name('related-api')

    def __init__(self, context):
        super().__init__(context)
        self.filter_id = None
        try:
            self.filter_id = self.context.topicpage_filter
        except Exception:
            pass

    def _get_documents(self, **kw):
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        try:
            current_article = zeit.content.article.interfaces.IArticle(
                self.context)
            uuid = ContentUUID(current_article)
            response = tms.get_related_documents(
                uuid=uuid.id,
                rows=self.context.teaser_amount,
                filtername=self.filter_id)
        except Exception as e:
            if e.status == 404:
                log.warning(
                    'TMSRelatedAPI error. No document with id %s',
                    uuid.id)
            else:
                log.warning(
                    'Error during TMSRelatedAPI for %s',
                    self.context.uniqueId, exc_info=True)
            return iter([])
        else:
            return iter(response)


class PreconfiguredQuery(ElasticsearchContentQuery):
    """Search via Elasticsearch."""

    grok.name('preconfigured-query')

    def __init__(self, context):
        super().__init__(context)
        factory = zeit.content.article.edit.interfaces.ITopicbox[
            'preconfigured_query'].source.factory
        self.query = {'query': factory.getQuery(context._preconfigured_query)}

    def _build_query(self):
        return self.query
