import copy
import lxml
from zeit.content.cp.interfaces import IAutomaticTeaserBlock
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

    query = zeit.cms.content.property.ObjectPathProperty(
        '.query.raw', zeit.content.cp.interfaces.IAutomaticRegion['query'])

    def __init__(self, context):
        self.context = context
        self.xml = self.context.xml
        self.__parent__ = self.context

    @property
    def automatic(self):
        return self._automatic

    @automatic.setter
    def automatic(self, value):
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

    def values(self):
        values = self.context.values()
        if self.automatic:
            result = []
            solr_result = list(zeit.find.search.search(
                self.query, sort_order='date-first-released desc',
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

    @property
    def rendered_xml(self):
        region = getattr(lxml.objectify.E, self.xml.tag)(**self.xml.attrib)
        region.attrib.pop('automatic', None)
        for block in self.values():
            if IAutomaticTeaserBlock.providedBy(block):
                region.append(block.rendered_xml)
            else:
                region.append(copy.copy(block.xml))
        return region


class AutomaticConfig(zeit.cms.content.dav.DAVPropertiesAdapter):

    zope.interface.implements(zeit.content.cp.interfaces.IAutomaticConfig)

    zeit.cms.content.dav.mapProperties(
        zeit.content.cp.interfaces.IAutomaticConfig,
        zeit.content.cp.interfaces.DAV_NAMESPACE,
        ('lead_candidate',))
