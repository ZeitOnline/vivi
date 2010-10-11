# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.lxml.interfaces
import lxml.objectify
import zeit.cms.content.property
import zeit.content.cp.centerpage
import zeit.content.cp.interfaces
import zeit.edit.interfaces
import zope.component
import zope.interface


class ElementFactory(object):
    """Base class for block factories."""

    zope.interface.implements(zeit.edit.interfaces.IElementFactory)

    def __init__(self, context):
        self.context = context

    def get_xml(self):
        container = lxml.objectify.E.container()
        container.set(
            '{http://namespaces.zeit.de/CMS/cp}type', self.element_type)
        container.set('module', self.module)
        return container

    def __call__(self):
        container = self.get_xml()
        content = zope.component.getMultiAdapter(
            (self.context, container),
            zeit.edit.interfaces.IElement,
            name=self.element_type)
        self.context.add(content)
        assert zeit.content.cp.centerpage.has_changed(self.context)
        return content


def elementFactoryFactory(adapts, element_type, title=None, module=None):
    """A factory which creates a content factory."""
    if module is None:
        module = element_type
    class_name = '%sFactory' % element_type.capitalize()
    factory = type(class_name, (ElementFactory,), dict(
        title=title,
        element_type=element_type,
        module=module))
    factory = zope.component.adapter(adapts)(factory)
    return factory


@zope.interface.implementer(zeit.content.cp.interfaces.ICenterPage)
@zope.component.adapter(zeit.edit.interfaces.IElement)
def cms_content_to_centerpage(context):
    return zeit.content.cp.interfaces.ICenterPage(context.__parent__, None)


class Element(zope.container.contained.Contained,
              zeit.cms.content.xmlsupport.Persistent):
    """Base class for blocks."""

    zope.interface.implements(zeit.edit.interfaces.IElement)

    zope.component.adapts(
        zeit.edit.interfaces.IContainer,
        gocept.lxml.interfaces.IObjectified)

    def __init__(self, context, xml):
        self.xml = xml
        # Set parent last so we don't trigger a write.
        self.__parent__ = context

    @property
    def __name__(self):
        return self.xml.get('{http://namespaces.zeit.de/CMS/cp}__name__')

    @__name__.setter
    def __name__(self, name):
        if name != self.__name__:
            self._p_changed = True
            self.xml.set('{http://namespaces.zeit.de/CMS/cp}__name__', name)

    @property
    def type(self):
        return self.xml.get('{http://namespaces.zeit.de/CMS/cp}type')

@zope.component.adapter(zeit.edit.interfaces.IElement)
@zope.interface.implementer(zeit.content.cp.interfaces.ICMSContentIterable)
def cms_content_iter(context):
    return iter([])


class Block(Element):

    title = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'title')

    publisher  = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'publisher')
    publisher_url = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'publisher_url')

    supertitle  = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'supertitle')
    supertitle_url = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'supertitle_url')

    read_more = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'read_more')
    read_more_url = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'read_more_url')
