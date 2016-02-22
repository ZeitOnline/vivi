from zeit.content.cp.interfaces import IAutomaticTeaserBlock
import logging
import zeit.content.cp.interfaces
import zeit.find.search
import zope.component
import zope.interface


log = logging.getLogger(__name__)


class AutomaticArea(zeit.cms.content.xmlsupport.Persistent):

    zope.component.adapts(zeit.content.cp.interfaces.IArea)
    zope.interface.implements(zeit.content.cp.interfaces.IRenderedArea)

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

    SOLR_FIELD = {
        'Channel': 'channels',
        'Keyword': 'keywords',
    }

    def _build_query(self):
        query = zeit.find.search.query(filter_terms=[
            zeit.solr.query.field_raw('published', 'published*')])
        conditions = []
        for type_, channel, subchannel in self.query:
            if subchannel:
                value = '%s*%s' % (channel, subchannel)
            else:
                # XXX Unclear whether this will work as desired for keywords.
                value = '%s*' % channel
            conditions.append(zeit.solr.query.field_raw(
                self.SOLR_FIELD[type_], value))
        if conditions:
            query = zeit.solr.query.and_(
                query, zeit.solr.query.or_(*conditions))
        return query

    def values(self):
        if not self.automatic:
            return self.context.values()

        self._v_try_to_retrieve_content = True
        self._v_retrieved_content = 0
        content = self._retrieve_content()
        result = []
        for block in self.context.values():
            if not IAutomaticTeaserBlock.providedBy(block):
                result.append(block)
                continue
            # This assumes that the *first* block always has a leader layout,
            # since otherwise the first result that may_be_leader might be
            # given to a non-leader block.
            if block.layout.id in ['leader', 'zon-large']:
                teaser = self._extract_newest(
                    content, predicate=is_lead_candidate)
                if teaser is None:
                    teaser = self._extract_newest(content)
                    block.change_layout(
                        zeit.content.cp.layout.get_layout('buttons'))
            else:
                teaser = self._extract_newest(content)
            if teaser is None:
                continue
            block.insert(0, teaser)
            result.append(block)

        return result

    def _retrieve_content(self):
        if not self._v_try_to_retrieve_content:
            return []
        if self.automatic_type == 'channel':
            content = self._query_solr(
                self._build_query(), self.query_order)
        elif self.automatic_type == 'query':
            content = self._query_solr(
                self.raw_query, self.raw_order)
        elif self.automatic_type == 'centerpage':
            content = self._query_centerpage()
        else:
            # BBB
            if self.raw_query:
                content = self._query_solr(
                    self.raw_query,
                    zeit.content.cp.interfaces.IArea['raw_order'].default)
            else:
                content = self._query_solr(
                    self._build_query(),
                    zeit.content.cp.interfaces.IArea['raw_order'].default)
        seen = self._v_retrieved_content
        self._v_retrieved_content += len(content)
        if self._v_retrieved_content > seen:
            self._v_try_to_retrieve_content = True
        else:
            self._v_try_to_retrieve_content = False
        return content

    def _query_solr(self, query, sort_order):
        result = []
        try:
            for item in zeit.find.search.search(
                    query, sort_order=sort_order,
                    start=self._v_retrieved_content,
                    rows=self.count_to_replace_duplicates):
                content = zeit.cms.interfaces.ICMSContent(
                    item['uniqueId'], None)
                if content is not None:
                    result.append(content)
        except:
            log.warning('Error during solr query %r for %s',
                        query, self.uniqueId, exc_info=True)
        return result

    def _query_centerpage(self):
        teasered = zeit.content.cp.interfaces.ITeaseredContent(
            self.referenced_cp, iter([]))
        result = []
        for i in range(
                self._v_retrieved_content + self.count_to_replace_duplicates):
            try:
                content = teasered.next()
            except StopIteration:
                # We've exhausted the available content.
                break
            if i >= self._v_retrieved_content:
                result.append(content)
        return result

    def _extract_newest(self, content, predicate=None):
        """Remove the first object from the content list for which predicate
        returns True; thus, the default predicate means: no filtering.
        """
        result = None
        pop = []
        cp = zeit.content.cp.interfaces.ICenterPage(self)
        for i, item in enumerate(content):
            if predicate is None or predicate(item):
                pop.append(item)
                if self.hide_dupes and (
                        cp.is_teaser_present_above(self.context, item)
                        or cp.is_teaser_manual_below(self.context, item)):
                    continue
                result = item
                break
        for item in pop:
            content.remove(item)
        if result is None and not content:
            # We've exhausted all available content due to duplicates, so we
            # need to retrieve some more.
            more_content = self._retrieve_content()
            if more_content:
                content[:] = more_content
                return self._extract_newest(content, predicate)
        return result

    def select_modules(self, *interfaces):
        for module in self.values():
            if any([x.providedBy(module) for x in interfaces]):
                yield module


def is_lead_candidate(content):
    metadata = zeit.cms.content.interfaces.ICommonMetadata(content, None)
    if metadata is None:
        return False
    return metadata.lead_candidate
