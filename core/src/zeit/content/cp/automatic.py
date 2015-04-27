from zeit.content.cp.interfaces import IAutomaticTeaserBlock
import grokcore.component as grok
import lxml.objectify
import zeit.cms.content.property
import zeit.content.cp.centerpage
import zeit.content.cp.interfaces
import zeit.find.search
import zope.component
import zope.interface


class AutomaticArea(zeit.cms.content.xmlsupport.Persistent):

    zope.component.adapts(zeit.content.cp.interfaces.IArea)
    zope.interface.implements(zeit.content.cp.interfaces.IAutomaticArea)

    _automatic = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'automatic',
        zeit.content.cp.interfaces.IAutomaticArea['automatic'])

    automatic_type = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'automatic_type',
        zeit.content.cp.interfaces.IAutomaticArea['automatic_type'])

    _count = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'count', zeit.content.cp.interfaces.IAutomaticArea['count'])

    referenced_cp = zeit.cms.content.property.SingleResource('.referenced_cp')

    hide_dupes = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'hide-dupes', zeit.content.cp.interfaces.IAutomaticArea[
            'hide_dupes'])

    raw_query = zeit.cms.content.property.ObjectPathProperty(
        '.raw_query', zeit.content.cp.interfaces.IAutomaticArea['raw_query'])

    MINIMUM_COUNT_TO_REPLACE_DUPLICATES = 5

    def __init__(self, context):
        self.context = context
        self.xml = self.context.xml
        self.__parent__ = self.context

        if 'hide-dupes' not in self.xml.attrib:
            self.hide_dupes = zeit.content.cp.interfaces.IAutomaticArea[
                'hide_dupes'].default

    @property
    def automatic(self):
        return self._automatic

    @automatic.setter
    def automatic(self, value):
        if self._automatic and not value:
            self._materialize_filled_values()
        self._automatic = value
        self._fill_with_placeholders()

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, value):
        self._count = value
        self._fill_with_placeholders()

    def _fill_with_placeholders(self):
        if self._automatic:
            for key in self.context:
                del self.context[key]
            for i in range(self.count):
                self.placeholder_factory()

    @property
    def count_to_replace_duplicates(self):
        return max(self.MINIMUM_COUNT_TO_REPLACE_DUPLICATES, 2 * self.count)

    @property
    def placeholder_factory(self):
        return zope.component.getAdapter(
            self.context, zeit.edit.interfaces.IElementFactory,
            name='auto-teaser')

    @property
    def query(self):
        if not hasattr(self.xml, 'query'):
            return ()

        result = []
        for condition in self.xml.query.getchildren():
            channel = unicode(condition)
            subchannel = None
            if ' ' in channel:
                channel, subchannel = channel.split(' ')
            result.append((condition.get('type'), channel, subchannel))
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
        self.xml.append(E.query(*[E.condition(
            '%s %s' % (channel, subchannel) if subchannel else channel,
            type=type_)
            for type_, channel, subchannel in value]))

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

    def _materialize_filled_values(self):
        order = self.context.keys()
        teaser_factory = zope.component.getAdapter(
            self.context, zeit.edit.interfaces.IElementFactory, name='teaser')
        for old in self.values():
            if not IAutomaticTeaserBlock.providedBy(old):
                continue
            items = reversed(list(old))
            new = teaser_factory()
            for content in items:
                new.insert(0, content)
            new.__name__ = old.__name__
            del self.context[old.__name__]
        # Preserve non-auto blocks.
        self.context.updateOrder(order)

        # Remove unfilled auto blocks.
        for block in list(self.context.values()):
            if IAutomaticTeaserBlock.providedBy(block):
                del self.context[block.__name__]


@grok.adapter(zeit.content.cp.interfaces.IArea)
@grok.implementer(zeit.content.cp.interfaces.ICMSContentIterable)
def cms_content_iter(context):
    wrapped_area = zeit.content.cp.interfaces.IAutomaticArea(context)
    if wrapped_area.automatic and wrapped_area.automatic_type == 'centerpage':
        yield wrapped_area.referenced_cp
    for content in zeit.content.cp.centerpage.cms_content_iter(wrapped_area):
        yield content
