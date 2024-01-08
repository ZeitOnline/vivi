import json
import logging

from zope.cachedescriptors.property import Lazy as cachedproperty
import grokcore.component as grok
import lxml
import requests
import zope.component
import zope.interface

from zeit.cms.content.cache import content_cache
from zeit.contentquery.configuration import CustomQueryProperty
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.article.article
import zeit.content.article.edit.interfaces
import zeit.content.cp.blocks.rss
import zeit.content.cp.blocks.teaser
import zeit.content.cp.interfaces
import zeit.retresco.content
import zeit.retresco.interfaces


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
        return self.context.start

    @property
    def rows(self):
        return self.context.count


@grok.adapter(zeit.contentquery.interfaces.IContentQuery)
@grok.implementer(zeit.cms.interfaces.ICMSContent)
def query_to_content(context):
    return zeit.cms.interfaces.ICMSContent(context.context, None)


class ElasticsearchContentQuery(ContentQuery):
    """Search via Elasticsearch."""

    grok.name('elasticsearch-query')

    include_payload = False  # Extension point for zeit.web and its LazyProxy.

    def __init__(self, context):
        super().__init__(context)
        self.query = json.loads(self.context.elasticsearch_raw_query or '{}')
        self.order_default = self.context.elasticsearch_raw_order

    @property
    def order(self):
        if not self.order_default:
            return None

        if isinstance(self.order_default, str):
            if 'random' in self.order_default:
                random_order = {
                    '_script': {
                        'type': 'number',
                        'script': {'lang': 'painless', 'source': 'Math.random()'},
                        'order': 'desc',  # descending into chaos, randomly
                    }
                }
                return random_order

            order_list = self.order_default.split(',')
            sort_orders = []
            for item in order_list:
                (field, order) = item.split(':')
                sort_orders.append({field: order})

            return sort_orders

        return None

    def __call__(self):
        self.total_hits = 0
        result = []

        try:
            query = self._build_query()
        except Exception:
            log.warning(
                'Error compiling elasticsearch query %r for %s',
                self.query,
                self.context.uniqueId,
                exc_info=True,
            )
            return result

        es = zope.component.getUtility(zeit.retresco.interfaces.IElasticsearch)
        try:
            response = es.search(
                query, start=self.start, rows=self.rows, include_payload=self.include_payload
            )
        except Exception as e:
            log.warning(
                'Error during elasticsearch query %r for %s',
                self.query,
                self.context.uniqueId,
                exc_info=True,
            )
            if 'Result window is too large' in str(e):
                # We have to determine the actually available number of hits.
                response = es.search(query, start=0, rows=0, include_payload=self.include_payload)
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
                query = {'query': {'bool': {'must': query, 'must_not': self.hide_dupes_clause}}}
        else:
            _query = self.query.get('query', {})
            if not isinstance(_query, list):
                _query = [_query]
            query = {
                'query': {
                    'bool': {
                        'filter': _query + self._additional_clauses,
                        'must_not': self._additional_not_clauses[:],
                    }
                }
            }
            if self.hide_dupes_clause:
                query['query']['bool']['must_not'].append(self.hide_dupes_clause)
        if self.order:
            query['sort'] = self.order
        return query

    _additional_clauses = [{'term': {'payload.workflow.published': True}}]

    _additional_not_clauses = [
        {'term': {'payload.zeit__DOT__content__DOT__gallery.type': 'inline'}}
    ]

    def _resolve(self, doc):
        return zeit.cms.interfaces.ICMSContent(
            zeit.cms.interfaces.ID_NAMESPACE[:-1] + doc['url'], None
        )

    @cachedproperty
    def hide_dupes_clause(self):
        """Perform de-duplication of results.

        Create an id query for teasers that already exist on the CP.
        """
        if not self.context.hide_dupes or not self.context.existing_teasers:
            return None
        ids = []
        for content in self.context.existing_teasers:
            id = getattr(zeit.cms.content.interfaces.IUUID(content, None), 'id', None)
            if id:
                ids.append(id)
        if not ids:
            return None
        return {'ids': {'values': ids}}


class CustomContentQuery(ElasticsearchContentQuery):
    grok.name('custom')

    ES_FIELD_NAMES = {
        'authorships': 'payload.head.authors',
        'channels': 'payload.document.channels.hierarchy',
        'content_type': 'doc_type',
    }

    serialize = CustomQueryProperty()._serialize_query_item

    def __init__(self, context):
        # Skip direct superclass, as we set `query` and `order` differently.
        super(ElasticsearchContentQuery, self).__init__(context)
        self.query = self._make_custom_query()
        self.order_default = self.context.query_order

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
                must.append({'bool': {'should': [self._make_clause(typ, x) for x in positive]}})
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
        typ, operator, value = self.serialize(self.context, item)
        return {'term': {self._fieldname(typ): value}}

    @classmethod
    def _fieldname(cls, typ):
        fieldname = cls.ES_FIELD_NAMES.get(typ)
        return fieldname if fieldname else cls._fieldname_from_property(typ)

    @classmethod
    def _fieldname_from_property(cls, typ):
        # XXX Generalize the class?
        prop = getattr(zeit.content.article.article.Article, typ)
        if not isinstance(prop, zeit.cms.content.dav.DAVProperty):
            raise ValueError('Cannot determine field name for %s', typ)
        return 'payload.%s.%s' % (
            zeit.retresco.content.davproperty_to_es(prop.namespace, prop.name)
        )

    def _make_ressort_condition(self, item):
        if item[3]:
            return {
                'bool': {
                    'must': [
                        {'term': {self._fieldname_from_property('ressort'): item[2]}},
                        {'term': {self._fieldname_from_property('sub_ressort'): item[3]}},
                    ]
                }
            }
        else:
            return {'term': {self._fieldname_from_property('ressort'): item[2]}}


class TMSContentQuery(ContentQuery):
    grok.name('topicpage')
    grok.baseclass()

    def __init__(self, context):
        super().__init__(context)
        self.topicpage = self.context.referenced_topicpage
        self.filter_id = self.context.topicpage_filter

    def __call__(self):
        result, _ = self._fetch(self.start)
        return result

    _teaser_count = NotImplemented

    def _fetch(self, start):
        """How hide_dupes works for TMS: Since the TMS API does not support
        passing dynamic ES query fragments (only statically configured
        "filters"), we cannot remove dupes server-side (like ESContentQuery
        does with its ``hide_dupes_clause``), but have to filter them here in
        code. And if we don't get enough teasers as our area wants
        (``self.context.count``) due to dropping some dupes, we have to fetch
        more from TMS.

        This is a separate method to ``__call__`` to provide an extension point
        for zeit.web, so it can handle hide_dupes when paginating:
        When rendering page>=2, we always have to also look at page 1, so that
        any dupes that have been dropped do not repeat on the later page.
        Thus zeit.web "peeks" with ``_fetch(start=0)``, and then adds the
        returned amount of dupes to the offset, ``_fetch(self.start+dupes)``.
        """
        cache = content_cache(self, 'topic_queries')
        rows = self._teaser_count + 5  # total teasers + some spares
        key = (self.topicpage, self.filter_id, start, self.order)
        if key in cache:
            response, start, _ = cache[key]
        else:
            response, hits = self._get_documents(start, rows)
            cache[key] = response, start, hits

        result = []
        dupes = 0
        while len(result) < self.rows:
            try:
                item = next(response)
            except StopIteration:
                start = start + rows  # fetch next batch
                response, hits = self._get_documents(start, rows)
                cache[key] = response, start, hits
                try:
                    item = next(response)
                except StopIteration:
                    break  # results are exhausted

            content = self._resolve(item)
            if content is None:
                continue
            if self.hide_dupes and content in self.context.existing_teasers:
                dupes += 1
            else:
                result.append(content)

        return result, dupes

    def _get_documents(self, start, rows):
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        try:
            response = tms.get_topicpage_documents(
                id=self.topicpage, filter=self.filter_id, order=self.order, start=start, rows=rows
            )
        except Exception as e:
            log.warning(
                'Error during TMS query %r for %s',
                self.topicpage,
                self.context.uniqueId,
                exc_info=True,
            )
            if 'Result window is too large' in str(e):
                # We have to determine the actually available number of hits.
                return self._get_documents(start=0, rows=0)
            return iter([]), 0
        else:
            return iter(response), response.hits

    def _resolve(self, doc):
        return zeit.cms.interfaces.ICMSContent(
            zeit.cms.interfaces.ID_NAMESPACE[:-1] + doc['url'], None
        )

    @property
    def hide_dupes(self):
        return self.context.hide_dupes

    @property
    def order(self):
        return zeit.retresco.content.KPI.FIELDS.get(
            self.context.topicpage_order, self.context.topicpage_order
        )

    @property
    def total_hits(self):
        cache = content_cache(self, 'tms_topic_queries')
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
        """We cache TMS responses on the CP (i.e. for the request), since for
        curated CPs users sometimes use multiple (small) auto areas that refer
        to the same ContentQuery. To hopefully prevent duplicate TMS requests,
        we collect all areas that target the same topicpage, and immediately
        request the summed amount of their counts (plus some spares, to
        hopefully account for dropped dupes).
        """
        cp = zeit.content.cp.interfaces.ICenterPage(self.context)
        return sum(
            a.count
            for a in cp.cached_areas
            if a.automatic
            and a.count
            and a.automatic_type == 'topicpage'
            and a.referenced_topicpage == self.topicpage
        )


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
        teasered = zeit.content.cp.interfaces.ITeaseredContent(self.context.referenced_cp, iter([]))
        result = []
        for content in teasered:
            if zeit.content.cp.blocks.rss.IRSSLink.providedBy(content):
                continue
            if self.context.hide_dupes and content in self.context.existing_teasers:
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
            content = self._get_feed(self.rss_feed.url, self.rss_feed.timeout)
            xml = lxml.etree.fromstring(content)
        except (requests.exceptions.RequestException, lxml.etree.XMLSyntaxError) as e:
            log.debug('Could not fetch feed {}: {}'.format(self.rss_feed.url, e))
            return []
        for item in xml.xpath('/rss/channel/item'):
            link = zeit.content.cp.blocks.rss.RSSLink(item, self.rss_feed)
            items.append(link)
        return items

    def _get_feed(self, url, timeout):
        return requests.get(url, timeout=timeout).content


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
                self.context.third_reference,
            ]
            return [ref for ref in references if ref]


class TMSRelatedApiQuery(TMSContentQuery):
    grok.name('related-api')

    # The TMS related API does not support `start`, so we cannot fetch
    # additional teasers to replace previously filtered-out duplicates.
    hide_dupes = False
    # The TMS related API currently does not support a custom order.
    order = None

    def _get_documents(self, start, rows):
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        try:
            content = zeit.cms.interfaces.ICMSContent(self)
            response = tms.get_related_documents(content, filter=self.filter_id, rows=rows)
        except Exception as e:
            if e.status == 404:
                log.warning('TMS related API did not find %s', self.context.uniqueId)
            else:
                log.warning(
                    'Error during TMSRelatedAPI for %s', self.context.uniqueId, exc_info=True
                )
            return iter([]), 0
        else:
            return iter(response), response.hits


class ArticleTMSRelatedApiQuery(TMSRelatedApiQuery):
    grok.context(zeit.content.article.edit.interfaces.ITopicbox)

    @property
    def _teaser_count(self):
        return self.context.count


class PreconfiguredQuery(ElasticsearchContentQuery):
    """Search via Elasticsearch."""

    grok.name('preconfigured-query')

    def __init__(self, context):
        super().__init__(context)
        factory = zeit.content.article.edit.interfaces.ITopicbox[
            'preconfigured_query'
        ].source.factory
        self.query = {'query': factory.getQuery(context.preconfigured_query)}

    def _build_query(self):
        return self.query


class TMSRelatedTopicsApiQuery(ContentQuery):
    grok.name('related-topics')
    grok.context(zeit.content.cp.interfaces.IArea)

    def __call__(self):
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        topics = tms.get_related_topics(self.context.related_topicpage, rows=self.rows)
        related_topics = []
        # TMS seems to return non existent/ redirecting topicpages
        for topic in topics:
            try:
                related_topics.append(zeit.cms.interfaces.ICMSContent(topic))
            except TypeError:
                log.warning('%s: Could not adapt %s to ICMSContent', self.__class__.__name__, topic)
                continue
        return related_topics


class TopicpageQuery(ContentQuery):
    grok.name('topicpagelist')

    def __call__(self):
        result = []
        topics = zope.component.getUtility(zeit.cms.tagging.interfaces.ITopicpages)
        direction = 'asc' if self.order == 'title' else 'desc'
        response = topics.get_topics(
            self.start, self.rows, sort_by=self.order, sort_order=direction
        )
        self.total_hits = response.hits
        for topic in response:
            result.append(self._resolve(topic))
        return result

    @property
    def order(self):
        return zeit.retresco.content.KPI.FIELDS.get(
            self.context.topicpagelist_order, self.context.topicpagelist_order
        )

    def _resolve(self, doc):
        config = zope.app.appsetup.product.getProductConfiguration('zeit.retresco')
        return zeit.cms.interfaces.ICMSContent(
            '%s%s/%s'
            % (zeit.cms.interfaces.ID_NAMESPACE[:-1], config['topicpage-prefix'], doc['id']),
            None,
        )


class ReachContentQuery(ContentQuery):
    grok.name('reach')
    grok.context(zeit.content.cp.interfaces.IArea)

    def __call__(self):
        reach = zope.component.getUtility(zeit.reach.interfaces.IReach)
        # XXX Converting to the format reach wants should probably be done by
        # IReach, but as that currently still needs bw-compat for z.w.site.
        # modules.buzzbox, and IReach is not used elsewhere, leave it for now.
        params = {}
        if self.context.reach_section:
            params['section'] = self.context.reach_section.lower()
        if self.context.reach_access:
            # reach does not support section if access is set (see reach docs)
            params.pop('section', None)
            params['access'] = self.context.reach_access
        if self.context.reach_age:
            params['maxAge'] = self.context.reach_age * 3600 * 24
        return reach.get_ranking(self.context.reach_service, limit=self.rows, **params)
