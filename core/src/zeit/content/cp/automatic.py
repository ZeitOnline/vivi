from zeit.content.cp.centerpage import writeabledict
from zeit.content.cp.interfaces import IAutomaticTeaserBlock
from zope.cachedescriptors.property import Lazy as cachedproperty
import grokcore.component as grok
import json
import logging
import operator
import zeit.cms.interfaces
import zeit.cms.content.interfaces
import zeit.content.cp.blocks.teaser
import zeit.content.cp.interfaces
import zeit.retresco.content
import zeit.retresco.interfaces
import zope.component
import zope.interface


log = logging.getLogger(__name__)


def centerpage_cache(context, name, factory=writeabledict):
    cp = zeit.content.cp.interfaces.ICenterPage(context)
    return cp.cache.setdefault(name, factory())


def cached_on_centerpage(keyfunc=operator.attrgetter('__name__'), attr=None):
    """ Decorator to cache the results of the function in a dictionary
        on the centerpage.  The dictionary keys are built using the optional
        `keyfunc`, which is called with `self` as a single argument. """
    def decorator(fn):
        def wrapper(self, *args, **kw):
            content = self.context
            cache = centerpage_cache(content, attr or fn.__name__)
            key = keyfunc(content)
            if key not in cache:
                cache[key] = fn(self, *args, **kw)
            return cache[key]
        return wrapper
    return decorator


class AutomaticArea(zeit.cms.content.xmlsupport.Persistent):

    zope.component.adapts(zeit.content.cp.interfaces.IArea)
    zope.interface.implements(zeit.content.cp.interfaces.IRenderedArea)

    start = 0  # Extension point for zeit.web to do pagination

    def __init__(self, context):
        self.context = context
        self.xml = self.context.xml
        self.__parent__ = self.context

    # Convenience: Delegate IArea to our context, so we can be used like one.
    def __getattr__(self, name):
        # There's no interface for xmlsupport.Persistent which could tell us
        # that this attribute needs special treatment.
        if name == '__parent__':
            return super(AutomaticArea, self).__getattr__(name)
        if name in zeit.content.cp.interfaces.IArea:
            return getattr(self.context, name)
        raise AttributeError(name)

    @cached_on_centerpage(attr='area_values')
    def values(self):
        if not self.automatic:
            return self.context.values()

        try:
            content = self._content_query()
        except LookupError:
            log.warning('%s found no IContentQuery type %s',
                        self.context, self.automatic_type)
            return self.context.values()

        result = []
        for block in self.context.values():
            if not IAutomaticTeaserBlock.providedBy(block):
                result.append(block)
                continue
            # This assumes that the *first* block always has a leader layout,
            # since otherwise the first result that may_be_leader might be
            # given to a non-leader block.
            if self.context.require_lead_candidates and block.layout.is_leader:
                teaser = pop_filter(content, is_lead_candidate)
                if teaser is None:
                    teaser = pop_filter(content)
                    block.change_layout(self.context.default_teaser_layout)
            else:
                teaser = pop_filter(content)
            if teaser is None:
                continue
            block.insert(0, teaser)
            result.append(block)

        return result

    @cachedproperty
    def _content_query(self):
        return zope.component.getAdapter(
            self, zeit.content.cp.interfaces.IContentQuery,
            name=self.automatic_type)

    def filter_values(self, *interfaces):
        # XXX copy&paste from zeit.edit.container.Base.filter_values
        for child in self.values():
            if any([x.providedBy(child) for x in interfaces]):
                yield child


def pop_filter(items, predicate=None):
    """Remove the first object from the list for which predicate returns True;
    no predicate means no filtering.
    """
    for i, item in enumerate(items):
        if predicate is None or predicate(item):
            items.pop(i)
            return item


def is_lead_candidate(content):
    metadata = zeit.cms.content.interfaces.ICommonMetadata(content, None)
    if metadata is None:
        return False
    return metadata.lead_candidate


class ContentQuery(grok.Adapter):

    grok.context(zeit.content.cp.interfaces.IRenderedArea)
    grok.implements(zeit.content.cp.interfaces.IContentQuery)
    grok.baseclass()

    total_hits = NotImplemented

    def __init__(self, context):
        self.context = context

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

    @property
    @cached_on_centerpage()
    def existing_teasers(self):
        current_area = self.context
        cp = zeit.content.cp.interfaces.ICenterPage(self.context)
        area_teasered_content = centerpage_cache(
            current_area, 'area_teasered_content')
        area_manual_content = centerpage_cache(
            current_area, 'area_manual_content')

        seen = set()
        above = True
        for area in cp.cached_areas:
            if area == current_area:
                above = False
            if above:  # automatic teasers above current area
                if area not in area_teasered_content:
                    area_teasered_content[area] = set(
                        zeit.content.cp.interfaces.ITeaseredContent(area))
                seen.update(area_teasered_content[area])
            else:  # manual teasers below (or in) current area
                if area not in area_manual_content:
                    # Probably not worth a separate adapter (like
                    # ITeaseredContent), since the use case is pretty
                    # specialised.
                    area_manual_content[area] = set(
                        zeit.content.cp.blocks.teaser.extract_manual_teasers(
                            area))
                seen.update(area_manual_content[area])
        return seen


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
            elasticsearch = zope.component.getUtility(
                zeit.retresco.interfaces.IElasticsearch)
            response = elasticsearch.search(
                self._build_query(), self.order,
                start=self.start, rows=self.rows,
                include_payload=self.include_payload)
            self.total_hits = response.hits
            for item in response:
                content = self._resolve(item)
                if content is not None:
                    result.append(content)
        except Exception:
            log.warning(
                'Error during elasticsearch query %r for %s',
                self.query, self.context.uniqueId, exc_info=True)
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
        if not self.context.hide_dupes or not self.existing_teasers:
            return None
        ids = []
        for content in self.existing_teasers:
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
        if typ == 'ressort':  # XXX Generalize to lookup instead of if?
            return self._make_ressort_condition(item)
        else:
            return self._make_condition(item)

    def _make_condition(self, item):
        typ, operator, value = self.context.context._serialize_query_item(item)
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

    def __init__(self, context):
        super(TMSContentQuery, self).__init__(context)
        self.topicpage = self.context.referenced_topicpage
        self.filter_id = self.context.topicpage_filter

    def __call__(self):
        result = []
        cache = centerpage_cache(self.context, 'tms_topic_queries')
        rows = self._teaser_count + 5           # total teasers + some spares
        key = (self.topicpage, self.filter_id, self.start)
        if key in cache:
            response, start, _ = cache[key]
        else:
            start = self.start
            response, hits = self._get_documents(start=start, rows=rows)
            cache[key] = response, start, hits
        while len(result) < self.rows:
            try:
                item = response.next()
            except StopIteration:
                start = start + rows            # fetch next batch
                response, hits = self._get_documents(start=start, rows=rows)
                cache[key] = response, start, hits
                try:
                    item = response.next()
                except StopIteration:
                    break                       # results are exhausted
            content = self._resolve(item)
            if content is not None and (not self.context.hide_dupes or
                                        content not in self.existing_teasers):
                result.append(content)
        return result

    def _get_documents(self, **kw):
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        try:
            response = tms.get_topicpage_documents(
                id=self.topicpage, filter=self.filter_id, **kw)
        except Exception:
            log.warning('Error during TMS query %r for %s',
                        self.topicpage, self.context.uniqueId, exc_info=True)
            return iter([]), 0
        else:
            return iter(response), response.hits

    def _resolve(self, doc):
        return zeit.cms.interfaces.ICMSContent(
            zeit.cms.interfaces.ID_NAMESPACE[:-1] + doc['url'], None)

    @property
    def _teaser_count(self):
        cp = zeit.content.cp.interfaces.ICenterPage(self.context)
        return sum(
            a.count for a in cp.cached_areas
            if a.automatic and a.count and a.automatic_type == 'topicpage' and
            a.referenced_topicpage == self.topicpage)

    @property
    def total_hits(self):
        cache = centerpage_cache(self.context, 'tms_topic_queries')
        key = (self.topicpage, self.filter_id, self.start)
        if key in cache:
            _, _, hits = cache[key]
        else:
            _, hits = self._get_documents(start=self.start, rows=0)
        return hits


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
            if self.context.hide_dupes and content in self.existing_teasers:
                continue
            result.append(content)
            if len(result) >= self.rows:
                break
        return result


import requests
import lxml


class RSSFeedContentQuery(ContentQuery):

    grok.name('rss-feed')

    def __call__(self):
        # Get the Feed and build ITeaseredContent stuff out of it
        feed_data = self._parse_feed()
        return []

    @property
    def rss_feed(self):
        return self.context.rss_feed

    def _parse_feed(self):
        try:
            response = requests.get(self.rss_feed.url,
                                    timeout=self.rss_feed.timeout)
            xml = lxml.etree.fromstring(response.content)
        except (requests.exceptions.RequestException,
                lxml.etree.XMLSyntaxError), e:
            log.debug('Could not fetch feed {}: {}'.format(
                self.rss_feed.url, e))
            return
        for item in xml.xpath('/rss/channel/item'):
            pass
