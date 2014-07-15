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
            solr_result = iter(zeit.find.search.search(
                self.query, sort_order='date-first-released desc'))
            for block in values:
                if not IAutomaticTeaserBlock.providedBy(block):
                    continue
                block.insert(0, zeit.cms.interfaces.ICMSContent(
                    solr_result.next()['uniqueId']))
        return values

    @property
    def rendered_xml(self):
        region = getattr(lxml.objectify.E, self.xml.tag)(**self.xml.attrib)
        for block in self.values():
            if IAutomaticTeaserBlock.providedBy(block):
                region.append(block.rendered_xml)
            else:
                region.append(copy.copy(block.xml))
        return region
