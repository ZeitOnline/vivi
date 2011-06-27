# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.lxml.interfaces
import grokcore.component as grok
import lxml.objectify
import sys
import zeit.cms.content.property
import zeit.content.cp.centerpage
import zeit.content.cp.interfaces
import zeit.edit.block
import zeit.edit.interfaces
import zope.component
import zope.interface


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
