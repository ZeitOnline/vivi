from zeit.content.cp.interfaces import IAutomaticTeaserBlock
import lxml.objectify
import zeit.cms.content.property
import zeit.content.cp.interfaces
import zeit.find.search
import zope.component
import zope.interface


class AutomaticRegion(zeit.cms.content.xmlsupport.Persistent):

    zope.component.adapts(zeit.content.cp.interfaces.IRegion)
    zope.interface.implements(zeit.content.cp.interfaces.IAutomaticRegion)

    _automatic = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'automatic',
        zeit.content.cp.interfaces.IAutomaticRegion['automatic'])

    _count = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'count', zeit.content.cp.interfaces.IAutomaticRegion['count'])

    raw_query = zeit.cms.content.property.ObjectPathProperty(
        '.raw_query', zeit.content.cp.interfaces.IAutomaticRegion['raw_query'])

    def __init__(self, context):
        self.context = context
        self.xml = self.context.xml
        self.__parent__ = self.context

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
        query = zeit.find.search.query(published='published')
        conditions = []
        for type_, channel, subchannel in self.query:
            if subchannel:
                value = '"%s %s"' % (channel, subchannel)
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
        if self.automatic:
            result = []
            query = self.raw_query if self.raw_query else self._build_query()
            solr_result = list(zeit.find.search.search(
                query, sort_order='date-first-released desc',
                additional_result_fields=['lead_candidate']))
            for block in values:
                if not IAutomaticTeaserBlock.providedBy(block):
                    result.append(block)
                    continue
                try:
                    # This assumes that the *first* block always has layout
                    # 'leader', since otherwise the first result that
                    # may_be_leader might be given to a non-leader block.
                    if block.layout.id == 'leader':
                        id = self._extract_leader(solr_result)
                    else:
                        id = solr_result.pop(0)['uniqueId']
                except IndexError:
                    continue
                block.insert(0, zeit.cms.interfaces.ICMSContent(id))
                result.append(block)
        else:
            result = values
        return result

    def _extract_leader(self, solr_result):
        for i, item in enumerate(solr_result):
            if item.get('lead_candidate'):
                solr_result.pop(i)
                return item['uniqueId']
        raise IndexError()

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
