# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.lxml.interfaces
import grokcore.component as grok
import lxml.objectify
import sys
import urlparse
import zeit.cms.content.xmlsupport
import zeit.edit.interfaces
import zope.component
import zope.interface
import zope.traversing.api


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

    def __eq__(self, other):
        if not zeit.edit.interfaces.IElement.providedBy(other):
            return False
        return self.xml == other.xml

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

    @property
    def uniqueId(self):
        parent = self.__parent__.uniqueId
        if not parent.startswith(zeit.edit.interfaces.BLOCK_NAMESPACE):
            return '%s%s#%s' % (
                zeit.edit.interfaces.BLOCK_NAMESPACE, parent, self.__name__)
        else:
            name = self.__name__
            if name is None:
                # XXX Since Container does not generally support index(),
                # this won't generally work. It's only implemented for
                # z.c.article.edit.Body at the moment.
                name = self.__parent__.index(self)
            return '%s/%s' % (parent, name)


@grok.adapter(
    basestring, name='http://block.vivi.zeit.de/')
@grok.implementer(zeit.cms.interfaces.ICMSContent)
def resolve_block_id(context):
    parts = urlparse.urlparse(context)
    assert parts.path.startswith('/')
    path = parts.path[1:]
    content = zeit.cms.cmscontent.resolve_wc_or_repository(path)
    return zope.traversing.api.traverse(content, parts.fragment)


class SimpleElement(Element):

    grok.baseclass()


@grok.adapter(zeit.edit.interfaces.IElement)
@grok.implementer(zeit.edit.interfaces.IArea)
def area_for_element(context):
    return zeit.edit.interfaces.IArea(context.__parent__, None)


class ElementFactory(object):
    """Base class for element factories."""

    zope.interface.implements(zeit.edit.interfaces.IElementFactory)

    def __init__(self, context):
        self.context = context

    def get_xml(self):
        raise NotImplementedError('Implemented in subclasses.')

    def __call__(self):
        container = self.get_xml()
        content = zope.component.getMultiAdapter(
            (self.context, container),
            zeit.edit.interfaces.IElement,
            name=self.element_type)
        self.context.add(content)
        return content


class TypeOnAttributeElementFactory(ElementFactory):

    tag_name = 'container'

    def get_xml(self):
        container = getattr(lxml.objectify.E, self.tag_name)()
        container.set(
            '{http://namespaces.zeit.de/CMS/cp}type', self.element_type)
        container.set('module', self.module)
        return container


def register_element_factory(
    adapts, element_type, title=None, module=None, frame=None,
    class_=TypeOnAttributeElementFactory,
    tag_name=TypeOnAttributeElementFactory.tag_name):
    if isinstance(adapts, zope.interface.interface.InterfaceClass):
        adapts = [adapts]
    if module is None:
        module = element_type
    if frame is None:
        frame = sys._getframe(1)

    for interface in adapts:
        name = '%s%sFactory' % (interface.__name__, element_type.capitalize())
        frame.f_locals[name] = create_factory_class(
            element_type, interface, name, frame.f_locals['__name__'],
            title, module, class_, tag_name)


def create_factory_class(element_type, adapts, name, module, title, cp_module,
                         class_, tag_name):
    class factory(grok.Adapter, class_):
        grok.context(adapts)
        grok.name(element_type)
    factory.title = title
    factory.element_type = element_type
    factory.module = cp_module
    factory.tag_name = tag_name
    factory.__name__ = name
    # so that the grokkers will pick it up
    factory.__module__ = module

    return factory


class UnknownBlock(SimpleElement):

    zope.interface.implements(zeit.edit.interfaces.IUnknownBlock)
    area = zeit.edit.interfaces.IArea
    type = '__unknown__'
