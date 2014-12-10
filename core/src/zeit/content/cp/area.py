# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

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

    supertitle = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'supertitle')
    teaserText = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'teaserText')
    background_color = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'background_color')

    type = 'area'

    # XXX fixme
    @property
    def layout(self):
        return zeit.content.cp.layout.get_bar_layout('parquet')

    @layout.setter
    def layout(self, value):
        pass  # XXX fixme

    @property
    def __name__(self):
        name = self.xml.get('area')
        if name == 'teaser-row-full':  # XXX backward compatibility for teaser bar
            return self.xml.get('{http://namespaces.zeit.de/CMS/cp}__name__')
        return name

    @__name__.setter
    def __name__(self, name):
        if name != self.__name__:
            self._p_changed = True
            area = self.xml.get('area')
            if area == 'teaser-row-full':
                self.xml.set('{http://namespaces.zeit.de/CMS/cp}__name__', name)
            self.xml.set('area', name)


class AreaFactory(zeit.edit.block.ElementFactory):

    # XML tags are named "region", thus do not change.
    tag_name = 'region'
    element_type = 'area'

    def get_xml(self):
        return getattr(lxml.objectify.E, self.tag_name)()


@grok.adapter(zeit.edit.interfaces.IElement)
@grok.implementer(zeit.content.cp.interfaces.IRegion)
def element_to_region(context):
    return zeit.content.cp.interfaces.IRegion(context.__parent__, None)


@grok.adapter(zeit.edit.interfaces.IElement)
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
