from zeit.content.cp.interfaces import IAutomaticTeaserBlock
from zope.cachedescriptors.property import Lazy as cachedproperty
import grokcore.component as grok
import json
import logging
import zeit.cms.interfaces
import zeit.cms.content.interfaces
import zeit.content.cp.interfaces
import zeit.find.search
import zeit.solr.interfaces
import zeit.solr.query
import zope.component
import zope.interface


log = logging.getLogger(__name__)


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

    @cachedproperty
    def existing_teasers(self):
        """Returns a set of ICMSContent objects that are already present on
        the CP in other areas. If IArea.hide_dupes is True, these should be
        not be repeated, and thus excluded from our query result.
        """
        cp = zeit.content.cp.interfaces.ICenterPage(self.context)
        result = set()
        result.update(cp.teasered_content_above(self.context))
        result.update(cp.manual_content_below(self.context))
        return result


class SolrContentQuery(ContentQuery):

    grok.name('query')

    FIELDS = ' '.join(zeit.find.search.DEFAULT_RESULT_FIELDS)

    def __init__(self, context):
        super(SolrContentQuery, self).__init__(context)
        self.query = self.context.raw_query
        self.order = self.context.raw_order

    def __call__(self):
        self.total_hits = 0
        result = []
        try:
            solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
            response = solr.search(
                self.query,
                sort=self.order,
                start=self.start,
                rows=self.rows,
                fl=self.FIELDS,
                fq=self.filter_query)
            self.total_hits = response.hits
            for item in response:
                content = self._resolve(item)
                if content is not None:
                    result.append(content)
        except Exception:
            log.warning(
                'Error during solr query %r for %s',
                self.query, self.context.uniqueId, exc_info=True)
        return result

    def _resolve(self, solr_result):
        return zeit.cms.interfaces.ICMSContent(solr_result['uniqueId'], None)

    @property
    def filter_query(self):
        """Performs deduplication of results. We basically add more conditions
        to the query to say "not this one or that one or those..." for all
        those teasers that already exist on the CP.
        """
        Q = zeit.solr.query
        if not self.context.hide_dupes or not self.existing_teasers:
            return Q.any_value()
        return Q.not_(Q.or_(*[Q._field('uniqueId', '"%s"' % x.uniqueId)
                              for x in self.existing_teasers]))


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
            query = {'query': {'bool': {
                'must': ([self.query.get('query', {})] +
                         self._additional_clauses)}}}
            if self.hide_dupes_clause:
                query['query']['bool']['must_not'] = self.hide_dupes_clause
        return query

    _additional_clauses = [
        {'term': {'payload.workflow.published': True}}
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
            return
        return {'ids': {'values': [zeit.cms.content.interfaces.IUUID(x).id
                                   for x in self.existing_teasers]}}


class ChannelContentQuery(ElasticsearchContentQuery):

    grok.name('channel')

    SOLR_TO_ES_SORT = {
        'date-last-published-semantic desc': (
            'payload.workflow.date_last_published_semantic:desc'),
        'last-semantic-change desc': (
            'payload.document.last-semantic-change:desc'),
        'date-first-released desc': (
            'payload.document.date_first_released:desc'),
    }

    def __init__(self, context):
        super(ElasticsearchContentQuery, self).__init__(context)
        self.query = self._make_channel_query()
        self.order = self.context.query_order
        if ' ' in self.order:  # BBB
            self.order = self.SOLR_TO_ES_SORT[self.order]

    def _make_channel_query(self):
        channels = []
        for channel, subchannel in self.context.query:
            value = channel
            if subchannel:
                value += ' ' + subchannel
            channels.append(value)
        return {'query': {'terms': {
            'payload.document.channels.hierarchy': channels}}}


class TMSContentQuery(ContentQuery):

    grok.name('topicpage')

    def __init__(self, context):
        super(TMSContentQuery, self).__init__(context)
        self.filter_id = self.context.topicpage_filter

    def __call__(self):
        self.total_hits = 0
        result = []
        topicpage = self.context.referenced_topicpage
        try:
            tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
            response = tms.get_topicpage_documents(
                topicpage, self.start, self.rows, filter=self.filter_id)
            self.total_hits = response.hits
            for item in response:
                content = self._resolve(item)
                if content is not None:
                    result.append(content)
        except Exception:
            log.warning('Error during TMS query %r for %s',
                        topicpage, self.context.uniqueId, exc_info=True)

        if not self.context.hide_dupes:
            return result
        # Since TMS does not allow extending a topicpage request with arbitrary
        # ES query parameters, we have to filter duplicates in-memory.
        return [x for x in result if x not in self.existing_teasers]

    def _resolve(self, doc):
        return zeit.cms.interfaces.ICMSContent(
            zeit.cms.interfaces.ID_NAMESPACE[:-1] + doc['url'], None)


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
