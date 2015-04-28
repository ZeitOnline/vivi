from zeit.content.cp.interfaces import IAutomaticTeaserBlock
import zeit.content.cp.interfaces
import zeit.find.search
import zope.component
import zope.interface


class AutomaticArea(zeit.cms.content.xmlsupport.Persistent):

    zope.component.adapts(zeit.content.cp.interfaces.IArea)
    zope.interface.implements(zeit.content.cp.interfaces.IRenderedArea)

    def __init__(self, context):
        self.context = context
        self.xml = self.context.xml
        self.__parent__ = self.context

    # Delegate everything to our context.
    def __getattr__(self, name):
        # There's no interface for xmlsupport.Persistent which could tell us
        # that this attribute needs special treatment.
        if name == '__parent__':
            return super(AutomaticArea, self).__getattr__(name)
        return getattr(self.context, name)

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
        values = self.context.values()
        if not self.automatic:
            return values

        if self.automatic_type == 'channel':
            teasers = self._query_solr(self._build_query())
        elif self.automatic_type == 'query':
            teasers = self._query_solr(self.raw_query)
        elif self.automatic_type == 'centerpage':
            teasers = self._query_centerpage()
        else:
            return values

        result = []
        for block in values:
            if not IAutomaticTeaserBlock.providedBy(block):
                result.append(block)
                continue
            # This assumes that the *first* block always has layout
            # 'leader', since otherwise the first result that
            # may_be_leader might be given to a non-leader block.
            if block.layout.id == 'leader':
                teaser = self._extract_newest(
                    teasers, predicate=lambda x: x.lead_candidate)
                if teaser is None:
                    teaser = self._extract_newest(teasers)
                    block.change_layout(
                        zeit.content.cp.layout.get_layout('buttons'))
            else:
                teaser = self._extract_newest(teasers)
            if teaser is None:
                continue
            block.insert(0, teaser)
            result.append(block)

        return result

    def _query_solr(self, query):
        return [zeit.cms.interfaces.ICMSContent(x['uniqueId'])
                for x in zeit.find.search.search(
                query, sort_order='date-first-released desc',
                rows=self.count_to_replace_duplicates)]

    def _query_centerpage(self):
        teasers = zeit.content.cp.interfaces.ITeaseredContent(
            self.referenced_cp, iter([]))
        result = []
        for i in range(self.count_to_replace_duplicates):
            try:
                result.append(teasers.next())
            except StopIteration:
                # We've exhausted the available teasers.
                break
        return result

    def _extract_newest(self, solr_result, predicate=lambda x: True):
        """Remove the first object from solr_result for which predicate returns
        True; thus, the default predicate means: no filtering.
        """
        result = None
        pop = []
        for i, item in enumerate(solr_result):
            if predicate(item):
                pop.append(item)
                if self.hide_dupes and zeit.content.cp.interfaces.ICenterPage(
                        self).is_teaser_present_above(self.context, item):
                    continue
                result = item
                break
        for item in pop:
            solr_result.remove(item)
        return result
