# -*- coding: utf-8 -*-
from zeit.cms.content.contentuuid import ContentUUID
from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.edit.interfaces import TopicReferenceSource
from zeit.content.article.interfaces import IArticle
from zeit.content.cp.automatic import cached_on_parent
from zope.cachedescriptors.property import Lazy as cachedproperty
import grokcore.component as grok
import itertools
import json
import logging
import lxml
import zeit.cms.content.reference
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.image.interfaces
import zope.component

log = logging.getLogger(__name__)


@grok.implementer(zeit.content.article.edit.interfaces.ITopicbox)
class Topicbox(zeit.content.article.edit.block.Block):

    type = 'topicbox'

    _count = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'count',
        zeit.content.article.edit.interfaces.ITopicbox['count'])

    _source_type = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'source_type',
        zeit.content.article.edit.interfaces.ITopicbox['source_type'])

    supertitle = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'supertitle',
        zeit.content.article.edit.interfaces.ITopicbox['supertitle'])

    title = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'title', zeit.content.article.edit.interfaces.ITopicbox['title'])

    link = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'link', zeit.content.article.edit.interfaces.ITopicbox['link'])

    link_text = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'link_text',
        zeit.content.article.edit.interfaces.ITopicbox['link_text'])

    first_reference = zeit.cms.content.reference.SingleResource(
        '.first_reference', 'related')

    second_reference = zeit.cms.content.reference.SingleResource(
        '.second_reference', 'related')

    third_reference = zeit.cms.content.reference.SingleResource(
        '.third_reference', 'related')

    elasticsearch_raw_query = zeit.cms.content.property.ObjectPathProperty(
        '.elasticsearch_raw_query',
        zeit.content.article.edit.interfaces.ITopicbox[
            'elasticsearch_raw_query'])

    elasticsearch_raw_order = zeit.cms.content.property.ObjectPathProperty(
        '.elasticsearch_raw_order',
        zeit.content.article.edit.interfaces.ITopicbox[
            'elasticsearch_raw_order'], use_default=True)

    is_complete_query = zeit.cms.content.property.ObjectPathProperty(
        '.elasticsearch_complete_query',
        zeit.content.article.edit.interfaces.ITopicbox[
            'is_complete_query'], use_default=True)

    centerpage = zeit.cms.content.property.SingleResource('.centerpage')

    source_type = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'source_type',
        zeit.content.article.edit.interfaces.ITopicbox['source_type'])

    topicpage = zeit.cms.content.property.ObjectPathProperty(
        '.topicpage',
        zeit.content.article.edit.interfaces.ITopicbox['topicpage'])

    topicpage_filter = zeit.cms.content.property.ObjectPathProperty(
        '.topicpage_filter',
        zeit.content.article.edit.interfaces.ITopicbox['topicpage_filter'])

    @property
    def source_type(self):
        result = self._source_type
        if not result:
            result = 'manuell'
        return result

    @source_type.setter
    def source_type(self, value):
        self._source_type = value

    @property
    def count(self):
        return 5
        return self._count

    @count.setter
    def count(self, value):
        self._count = 5
        if not value:
            self._count = 5
        else:
            self._count = value

    @property
    def _reference_properties(self):
        return (self.first_reference,
                self.second_reference,
                self.third_reference)

    @property
    def referenced_cp(self):
        if not self.source_type == 'manuell':
            return None
        import zeit.content.cp.interfaces
        if zeit.content.cp.interfaces.ICenterPage.providedBy(
                self.first_reference):
            return self.first_reference

    @cached_on_parent(IArticle, 'topicbox_values')
    def values(self):
        if self.referenced_cp:
            parent_article = zeit.content.article.interfaces.IArticle(self,
                                                                      None)
            return itertools.islice(
                filter(lambda x: x != parent_article,
                       zeit.edit.interfaces.IElementReferences(
                           self.referenced_cp)),
                len(self._reference_properties))

        if self.source_type == 'manuell':
            return (
                content for content in self._reference_properties if content)

        try:
            filtered_content = []
            content = iter(self._content_query())

            if content is None:
                return ()

            while(len(filtered_content)) < 3:
                try:
                    item = next(content)
                    if item in filtered_content:
                        continue
                    allow_cp = self.source_type == 'centerpage'
                    if TopicReferenceSource(
                            allow_cp).verify_interface(item):
                        filtered_content.append(item)
                except StopIteration:
                    break
            return iter(filtered_content)

        except (LookupError, ValueError):
            log.warning('found no IContentQuery type %s',
                        self.source_type)
            return (
                content for content in self._reference_properties if content)

    @property
    def _content_query(self):
        content = zope.component.getAdapter(
            self, zeit.content.article.edit.interfaces.IContentQuery,
            name=self.source_type or '')
        return content

    @property
    def query(self):
        if not hasattr(self.xml, 'query'):
            return ()

        result = []
        for condition in self.xml.query.getchildren():
            typ = condition.get('type')
            if typ == 'Channel':  # BBB
                typ = 'channels'
            operator = condition.get('operator')
            if not operator:  # BBB
                operator = 'eq'
            value = self._converter(typ).fromProperty(str(condition))
            field = zeit.content.cp.interfaces.IArea[
                'query'].value_type.type_interface[typ]
            if zope.schema.interfaces.ICollection.providedBy(field):
                value = value[0]
            # CombinationWidget needs items to be flattened
            if not isinstance(value, tuple):
                value = (value,)
            result.append((typ, operator) + value)
        return tuple(result)

    @query.setter
    def query(self, value):
        try:
            self.xml.remove(self.xml.query)
        except AttributeError:
            pass

        if not value:
            return

        E = lxml.objectify.E
        query = E.query()
        for item in value:
            typ, operator, val = self._serialize_query_item(item)
            query.append(E.condition(val, type=typ, operator=operator))
        self.xml.append(query)

    def _serialize_query_item(self, item):
        typ = item[0]
        operator = item[1]
        field = zeit.content.cp.interfaces.IArea[
            'query'].value_type.type_interface[typ]

        if len(item) > self.count:
            value = item[2:]
        else:
            value = item[2]
        if zope.schema.interfaces.ICollection.providedBy(field):
            value = field._type((value,))  # tuple(already_tuple) is a no-op
        value = self._converter(typ).toProperty(value)

        return typ, operator, value

    def _converter(self, selector):
        field = zeit.content.cp.interfaces.IArea[
            'query'].value_type.type_interface[selector]
        field = field.bind(zeit.content.article.interfaces.IArticle(self))
        props = zeit.cms.content.property.DAVConverterWrapper.DUMMY_PROPERTIES
        return zope.component.getMultiAdapter(
            (field, props),
            zeit.cms.content.interfaces.IDAVPropertyConverter)


@zope.component.adapter(zeit.content.article.edit.interfaces.ITopicbox)
@zope.interface.implementer(zeit.content.image.interfaces.IImages)
class TopicboxImages(zeit.cms.related.related.RelatedBase):

    image = zeit.cms.content.reference.SingleResource('.image', 'image')

    fill_color = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.image', 'fill_color',
        zeit.content.image.interfaces.IImages['fill_color'])


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = Topicbox
    title = _('Topicbox')


@grok.implementer(zeit.content.article.edit.interfaces.IContentQuery)
class ContentQuery(grok.Adapter):

    grok.context(zeit.content.article.edit.interfaces.ITopicbox)
    grok.baseclass()

    total_hits = NotImplemented

    def __init__(self, context):
        self.context = context

    def __call__(self):
        raise NotImplementedError()

    @property
    def existing_teasers(self):
        # ToDo: Compare current teaser uniqueId with
        # predecessors to avoid dupes.
        return []


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
                query, self.order, rows=self.context.count,
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
        else:
            _query = self.query.get('query', {})
            if not isinstance(_query, list):
                _query = [_query]
            query = {'query': {'bool': {
                'filter': _query + self._additional_clauses,
                'must_not': self._additional_not_clauses[:]}}}
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


class TMSContentQuery(ContentQuery):

    grok.name('topicpage')

    def __init__(self, context):
        super(TMSContentQuery, self).__init__(context)
        self.topicpage = self.context.topicpage
        self.filter_id = self.context.topicpage_filter

    def __call__(self):
        result, _ = self._fetch(start=0)
        return result

    def _fetch(self, start):
        """Extension point for zeit.web to do pagination and de-duping."""

        # cache = centerpage_cache(self.context, 'tms_topic_queries')
        cache = {}

        # total teasers + some spares
        rows = self._teaser_count + self.context.count
        key = (self.topicpage, self.filter_id, start)
        if key in cache:
            response, start, _ = cache[key]
        else:
            response, hits = self._get_documents(
                start=start,
                rows=self.context.count)
            cache[key] = response, start, hits

        result = []
        dupes = 0
        while len(result) < self.context.count:
            try:
                item = next(response)
            except StopIteration:
                start = start + rows            # fetch next batch
                response, hits = self._get_documents(
                    start=start,
                    rows=self.context.count)
                cache[key] = response, start, hits
                try:
                    item = next(response)
                except StopIteration:
                    break                       # results are exhausted

            content = self._resolve(item)
            if content is None:
                continue

            if content in self.existing_teasers:
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
    def _teaser_count(self):
        return 3

        cp = zeit.content.cp.interfaces.ICenterPage(self.context)
        return sum(
            a.count for a in cp.cached_areas
            if a.automatic and a.count and a.automatic_type == 'topicpage' and
            a.referenced_topicpage == self.topicpage)

    @property
    def total_hits(self):
        # cache = centerpage_cache(self.context, 'tms_topic_queries')
        cache = {}
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
            self.context.centerpage, iter([]))
        result = []
        for content in teasered:
            if zeit.content.cp.blocks.rss.IRSSLink.providedBy(content):
                continue
            result.append(content)

            if len(result) >= self.context.count:
                break
        return result


class TMSRelatedApiQuery(TMSContentQuery):

    grok.name('related-api')

    def __init__(self, context):
        super(TMSRelatedApiQuery, self).__init__(context)

    def _get_documents(self, **kw):
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        try:
            current_article = zeit.content.article.interfaces.IArticle(
                self.context)
            uuid = ContentUUID(current_article)
            response = tms.get_related_documents(
                uuid=uuid.id, rows=self.context.count)
        except Exception as e:
            if e.status == 404:
                log.warning(
                    'TMSRelatedAPI error. No document with id %s',
                    uuid.id)
            else:
                log.warning(
                    'Error during TMSRelatedAPI for %s',
                    self.context.uniqueId, exc_info=True)
            return iter([]), 0
        else:
            return iter(response), response.hits
