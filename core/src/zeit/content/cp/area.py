# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.lxml.interfaces
import grokcore.component as grok
import itertools
import lxml
import zeit.content.cp.interfaces
import zeit.edit.container
import zope.component
import zope.interface


@zope.component.adapter(zeit.edit.interfaces.IArea)
@zope.interface.implementer(zeit.content.cp.interfaces.ICMSContentIterable)
def cms_content_iter(context):
    return itertools.chain(*[
        zeit.content.cp.interfaces.ICMSContentIterable(block)
        for block in context.values()
        if block is not None])


@grok.adapter(zeit.content.cp.interfaces.ISection)  # maybe use IContainer for both
@grok.implementer(zeit.content.cp.interfaces.ICMSContentIterable)
def cms_content_iter_for_section(context):
    return itertools.chain(*[
        zeit.content.cp.interfaces.ICMSContentIterable(block)
        for block in context.values()
        if block is not None])


class Area(zeit.edit.container.TypeOnAttributeContainer):

    zope.interface.implements(zeit.content.cp.interfaces.IArea)
    zope.component.adapts(
        zeit.content.cp.interfaces.ISection,
        gocept.lxml.interfaces.IObjectified)

    type = 'area'

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

    tag_name = 'region'  # XXX actually "area"

    def get_xml(self):
        return getattr(lxml.objectify.E, self.tag_name)()


class Section(zeit.edit.container.Base):

    zope.interface.implements(zeit.content.cp.interfaces.ISection)
    zope.component.adapts(
        zeit.content.cp.interfaces.ICenterPage,
        gocept.lxml.interfaces.IObjectified)

    _find_item = lxml.etree.XPath('./*[@area = $name or @cms:__name__ = $name]',
        namespaces=dict(cms='http://namespaces.zeit.de/CMS/cp'))
    # _get_keys = lxml.etree.XPath('./*/attribute::area')

    type = 'area'

    @property
    def __name__(self):
        return self.xml.get('area')

    @__name__.setter
    def __name__(self, name):
        if name != self.__name__:
            self._p_changed = True
            self.xml.set('area', name)

    def _get_element_type(self, xml_node):
        if xml_node.get('area') == 'teaser-row-full':  # XXX backward compatibility for teaser bar
            return xml_node.get('{http://namespaces.zeit.de/CMS/cp}type')
        return xml_node.tag

    def __getitem__(self, key):
        area = super(Section, self).__getitem__(key)
        if key == 'lead':
            zope.interface.alsoProvides(
                area, zeit.content.cp.interfaces.ILead)
        if key == 'informatives':
            zope.interface.alsoProvides(
                area, zeit.content.cp.interfaces.IInformatives)
        return area

    def _get_keys(self, xml):
        keys = []
        for child in xml.getchildren():
            key = child.get('area')
            if key == 'teaser-row-full':
                key = child.get('{http://namespaces.zeit.de/CMS/cp}__name__')
            keys.append(key)
        return keys


class SectionFactory(zeit.edit.block.ElementFactory):

    tag_name = 'cluster'  # XXX actually "region"

    def get_xml(self):
        return getattr(lxml.objectify.E, self.tag_name)()


@zope.interface.implementer(zeit.content.cp.interfaces.ICenterPage)
@zope.component.adapter(zeit.edit.interfaces.IContainer)
def container_to_centerpage(context):
    # Is this required? Is there any IContainer which is not an IElement at the
    # same time?
    return zeit.content.cp.interfaces.ICenterPage(context.__parent__, None)


@grok.adapter(zeit.edit.interfaces.IElement)
@grok.implementer(zeit.content.cp.interfaces.ISection)
def element_to_section(context):
    return zeit.content.cp.interfaces.ISection(context.__parent__, None)


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


@grok.adapter(zeit.content.cp.interfaces.IMosaic)
@grok.implementer(zeit.content.cp.interfaces.IRenderedXML)
def rendered_xml_mosaic(context):
    root = getattr(lxml.objectify.E, context.xml.tag)(**context.xml.attrib)
    for item in context.values():
        root.append(zeit.content.cp.interfaces.IRenderedXML(item))
    return root
