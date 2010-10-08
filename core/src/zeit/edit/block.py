# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.lxml.interfaces
import grokcore.component
import lxml.objectify
import zeit.cms.content.property
import zeit.edit.interfaces
import zope.component
import zope.interface




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


@grokcore.component.adapter(zeit.edit.interfaces.IElement)
@grokcore.component.implementer(zeit.edit.interfaces.IArea)
def area_for_element(context):
    return zeit.edit.interfaces.IArea(context.__parent__, None)
