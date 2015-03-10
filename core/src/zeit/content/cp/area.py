from zeit.cms.i18n import MessageFactory as _
import fractions
import gocept.lxml.interfaces
import grokcore.component as grok
import lxml
import zeit.cms.content.property
import zeit.content.cp.interfaces
import zeit.edit.container
import zope.component
import zope.interface


class Region(zeit.edit.container.Base):

    zope.interface.implements(zeit.content.cp.interfaces.IRegion)
    zope.component.adapts(
        zeit.content.cp.interfaces.IBody,
        gocept.lxml.interfaces.IObjectified)

    _find_item = lxml.etree.XPath(
        './*[@area = $name or @cms:__name__ = $name]',
        namespaces=dict(cms='http://namespaces.zeit.de/CMS/cp'))

    type = 'region'

    title = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'title')

    @property
    def __name__(self):
        return self.xml.get('area')

    @__name__.setter
    def __name__(self, name):
        if name != self.__name__:
            self._p_changed = True
            self.xml.set('area', name)

    def _get_element_type(self, xml_node):
        return 'area'

    def _get_keys(self, xml):
        keys = []
        for child in xml.getchildren():
            key = child.get('area')
            if key == 'teaser-row-full':
                key = child.get('{http://namespaces.zeit.de/CMS/cp}__name__')
            keys.append(key)
        return keys


class RegionFactory(zeit.edit.block.ElementFactory):

    # XML tags are named "cluster", thus do not change.
    tag_name = 'cluster'
    element_type = 'region'

    def get_xml(self):
        return getattr(lxml.objectify.E, self.tag_name)()


class Area(zeit.edit.container.TypeOnAttributeContainer):

    zope.interface.implements(zeit.content.cp.interfaces.IArea)
    zope.component.adapts(
        zeit.content.cp.interfaces.IRegion,
        gocept.lxml.interfaces.IObjectified)

    _layout = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'module')
    supertitle = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'supertitle')
    title = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'title')
    _width = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'width')
    teaserText = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'teaserText')
    background_color = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'background_color')
    block_max = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'block_max', zeit.content.cp.interfaces.IArea['block_max'])
    _overflow_into = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'overflow_into')

    type = 'area'

    @property
    def is_teaserbar(self):
        # backward compatibility for teaser bar
        return self.xml.get('area') == 'teaser-row-full'

    @property
    def layout(self):
        for layout in zeit.content.cp.interfaces.IArea['layout'].source(self):
            if layout.id == self._layout:
                return layout
        return zeit.content.cp.interfaces.IArea['layout'].default

    @layout.setter
    def layout(self, value):
        self._layout = value.id

    @property
    def width(self):
        # XXX since we hard code the default values for backward compatibility,
        # this also makes it mandatory to have according rules in the width
        # source definition
        if self.is_teaserbar:
            return '1/1'
        if self.__name__ == 'informatives':
            return '1/3'
        if self.__name__ == 'lead':
            return '2/3'
        return self._width or '1/1'

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def width_fraction(self):
        numerator, denominator = [int(x) for x in self.width.split('/')]
        return fractions.Fraction(numerator, denominator)

    @property
    def overflow_into(self):
        if self._overflow_into is None:
            return None
        return zeit.content.cp.interfaces.ICenterPage(self).get_recursive(
            self._overflow_into)

    @overflow_into.setter
    def overflow_into(self, value):
        if value is None:
            self._overflow_into = None
        self._overflow_into = value.__name__

    @property
    def __name__(self):
        name = self.xml.get('area')
        if self.is_teaserbar:
            return self.xml.get('{http://namespaces.zeit.de/CMS/cp}__name__')
        return name

    @__name__.setter
    def __name__(self, name):
        if name != self.__name__:
            self._p_changed = True
            if self.is_teaserbar:
                self.xml.set('{http://namespaces.zeit.de/CMS/cp}__name__', name)
            self.xml.set('area', name)


class AreaFactory(zeit.edit.block.ElementFactory):

    # XML tags are named "region", thus do not change.
    tag_name = 'region'
    element_type = 'area'
    title = _('Area')

    def get_xml(self):
        return getattr(lxml.objectify.E, self.tag_name)()


@grok.adapter(zeit.content.cp.interfaces.IElement)
@grok.implementer(zeit.content.cp.interfaces.IRegion)
def element_to_region(context):
    return zeit.content.cp.interfaces.IRegion(context.__parent__, None)


@grok.adapter(zeit.content.cp.interfaces.IElement)
@grok.implementer(zeit.content.cp.interfaces.IArea)
def element_to_area(context):
    return zeit.content.cp.interfaces.IArea(context.__parent__, None)


@grok.adapter(zeit.content.cp.interfaces.IRegion)
@grok.implementer(zeit.edit.interfaces.IArea)
def region_to_area(context):
    """A region *contains*, areas."""
    return None


@grok.adapter(zeit.content.cp.interfaces.IRegion)
@grok.implementer(zeit.content.cp.interfaces.IRenderedXML)
def rendered_xml_mosaic(context):
    root = getattr(lxml.objectify.E, context.xml.tag)(**context.xml.attrib)
    for item in context.values():
        root.append(zeit.content.cp.interfaces.IRenderedXML(item))
    return root


@grok.adapter(zeit.content.cp.interfaces.IArea)
@grok.implementer(zeit.content.cp.interfaces.IRenderedXML)
def rendered_xml(context):
    area = getattr(lxml.objectify.E, context.xml.tag)(**context.xml.attrib)
    area.attrib.pop('automatic', None)
    # XXX This API is non-obvious: IAutomaticArea also works for areas
    # that are not or can never be automatic.
    for block in zeit.content.cp.interfaces.IAutomaticArea(context).values():
        area.append(zeit.content.cp.interfaces.IRenderedXML(block))
    return area


@grok.subscribe(
    zeit.content.cp.interfaces.IBlock,
    zope.container.interfaces.IObjectAddedEvent)
def overflow_blocks(context, event):
    area = context.__parent__
    if (area.block_max is None
        or len(area) <= area.block_max
        or area.overflow_into is None):
        return

    # Since IContainer.add only appends, the newly added block is at -1,
    # while the previously last block is at -2.
    last_block = area.values()[-2]
    del area[last_block.__name__]
    area.overflow_into.add(last_block)
    keys = area.overflow_into.keys()
    area.overflow_into.updateOrder([keys[-1]] + keys[:-1])
