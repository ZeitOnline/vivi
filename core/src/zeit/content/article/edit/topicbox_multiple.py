# -*- coding: utf-8 -*-
from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
from zeit.content.cp.centerpage import writeabledict
import zeit.cms.content.reference
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zope.component
from zope.cachedescriptors.property import Lazy as cachedproperty
import lxml
import json
import requests
import logging

log = logging.getLogger(__name__)


def centerpage_cache(context, name, factory=writeabledict):
    cp = zeit.content.cp.interfaces.ICenterPage(context)
    return cp.cache.setdefault(name, factory())


class ReferencedCpFallbackProperty(
        zeit.cms.content.property.ObjectPathProperty):
    """
    Special ObjectPathProperty which looks up an attribute
    from the referenced cp as a fallback.
    """

    def __get__(self, instance, class_):
        value = super(ReferencedCpFallbackProperty, self).__get__(
            instance, class_)
        if value == self.field.missing_value and instance.referenced_cp:
            value = getattr(instance.referenced_cp,
                            self.field.__name__,
                            self.field.default)
        return value


@grok.implementer(zeit.content.article.edit.interfaces.ITopicboxMultiple)
class TopicboxMultiple(zeit.content.article.edit.block.Block):

    type = 'topicbox_multiple'

    _source = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'source',
        zeit.content.article.edit.interfaces.ITopicboxMultiple['source'])

    _source_type = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'source_type',
        zeit.content.article.edit.interfaces.ITopicboxMultiple['source_type'])

    _centerpage = zeit.cms.content.property.SingleResource('.centerpage')

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        self._source = value
        if value:
            self._set_references()

    @property
    def source_type(self):
        result = self._source_type
        if result == 'channel':  # BBB
            result = 'custom'
        return result

    @source_type.setter
    def source_type(self, value):
        self._source_type = value

    _count = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'count',
        zeit.content.article.edit.interfaces.ITopicboxMultiple['count'])

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, value):
        if not value:
            self._count = 3
        else:
            self._count = value

    @property
    def centerpage(self):
        return self._centerpage

    @centerpage.setter
    def centerpage(self, value):
        # It is still possible to build larger circles (e.g A->C->A)
        # but a sane user should not ignore the errormessage shown in the
        # cp-editor and preview.
        # Checking for larger circles is not reasonable here.
        if value is not None:
            if value.uniqueId == \
                    zeit.content.article.interfaces.IArticle(self).uniqueId:
                raise ValueError("A centerpage can't reference itself!")
        self._centerpage = value

    supertitle = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'supertitle',
        zeit.content.article.edit.interfaces.ITopicboxMultiple['supertitle'])

    title = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'title',
        zeit.content.article.edit.interfaces.ITopicboxMultiple['title'])

    link = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'link',
        zeit.content.article.edit.interfaces.ITopicboxMultiple['link'])

    link_text = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'link_text',
        zeit.content.article.edit.interfaces.ITopicboxMultiple['link_text'])

    first_reference = zeit.cms.content.reference.SingleResource(
        '.first_reference', 'related')

    second_reference = zeit.cms.content.reference.SingleResource(
        '.second_reference', 'related')

    third_reference = zeit.cms.content.reference.SingleResource(
        '.third_reference', 'related')

    query = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'query',
        zeit.content.article.edit.interfaces.ITopicboxMultiple['query'])

    query_order = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'query_order',
        zeit.content.article.edit.interfaces.ITopicboxMultiple['query_order'])

    hide_dupes = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'hide-dupes',
        zeit.content.article.edit.interfaces.ITopicboxMultiple['hide_dupes'],
        use_default=True)

    elasticsearch_raw_query = zeit.cms.content.property.ObjectPathProperty(
        '.elasticsearch_raw_query',
        zeit.content.article.edit.interfaces.ITopicboxMultiple[
            'elasticsearch_raw_query'])

    elasticsearch_raw_order = zeit.cms.content.property.ObjectPathProperty(
        '.elasticsearch_raw_order',
        zeit.content.article.edit.interfaces.ITopicboxMultiple[
            'elasticsearch_raw_order'], use_default=True)

    is_complete_query = zeit.cms.content.property.ObjectPathProperty(
        '.elasticsearch_complete_query',
        zeit.content.article.edit.interfaces.ITopicboxMultiple[
            'is_complete_query'], use_default=True)

    topicpage = zeit.cms.content.property.ObjectPathProperty(
        '.topicpage',
        zeit.content.article.edit.interfaces.ITopicboxMultiple['topicpage'])

    topicpage_filter = zeit.cms.content.property.ObjectPathProperty(
        '.topicpage_filter',
        zeit.content.article.edit.interfaces.ITopicboxMultiple[
            'topicpage_filter'])

    is_complete_query = zeit.cms.content.property.ObjectPathProperty(
        '.elasticsearch_complete_query',
        zeit.content.article.edit.interfaces.ITopicboxMultiple[
            'is_complete_query'],
        use_default=True)

    rss_feed = zeit.cms.content.property.DAVConverterWrapper(
        zeit.cms.content.property.ObjectPathAttributeProperty('.', 'rss_feed'),
        zeit.content.article.edit.interfaces.ITopicboxMultiple['rss_feed'])

    topiclink_label_1 = ReferencedCpFallbackProperty(
        '.topiclink_label_1',
        zeit.content.cp.interfaces.IArea['topiclink_label_1'])

    topiclink_url_1 = ReferencedCpFallbackProperty(
        '.topiclink_url_1',
        zeit.content.cp.interfaces.IArea['topiclink_url_1'])

    topiclink_label_2 = ReferencedCpFallbackProperty(
        '.topiclink_label_2',
        zeit.content.cp.interfaces.IArea['topiclink_label_2'])

    topiclink_url_2 = ReferencedCpFallbackProperty(
        '.topiclink_url_2',
        zeit.content.cp.interfaces.IArea['topiclink_url_2'])

    topiclink_label_3 = ReferencedCpFallbackProperty(
        '.topiclink_label_3',
        zeit.content.cp.interfaces.IArea['topiclink_label_3'])

    topiclink_url_3 = ReferencedCpFallbackProperty(
        '.topiclink_url_3',
        zeit.content.cp.interfaces.IArea['topiclink_url_3'])

    def _set_references(self):
        # Set the three references fields to Content Query result.

        for val in self.values:
            if self.first_reference is None:
                self.first_reference = val
            elif self.second_reference is None:
                self.second_reference = val
            elif self.third_reference is None:
                self.third_reference = val

    @property
    def values(self):
        if not self._source:
            return [
                self.first_reference,
                self.second_reference,
                self.third_reference]

        try:
            content = self._content_query()
            return content

        except (LookupError, ValueError):
            log.warning('%s found no IContentQuery type %s',
                        self.context, self.source_type)
            return [
                self.first_reference,
                self.second_reference,
                self.third_reference]

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

        if len(item) > 3:
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


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = TopicboxMultiple
    title = _('Topicbox Multiple')


@grok.implementer(zeit.content.article.edit.interfaces.IContentQuery)
class ContentQuery(grok.Adapter):

    grok.context(zeit.content.article.edit.interfaces.ITopicboxMultiple)
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
    def existing_teasers(self):
        # ToDo: Compare current teaser uniqueId with
        # predecessors to avoid dupes.
        return False


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
        result, _ = self._fetch(self.start)
        return result

    def _fetch(self, start):
        """Extension point for zeit.web to do pagination and de-duping."""

        cache = centerpage_cache(self.context, 'tms_topic_queries')
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
            if self.context.hide_dupes and content in self.existing_teasers:
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
            self.context.centerpage, iter([]))
        result = []
        for content in teasered:
            if zeit.content.cp.blocks.rss.IRSSLink.providedBy(content):
                continue
            result.append(content)
            if len(result) >= self.rows:
                break
        return result
