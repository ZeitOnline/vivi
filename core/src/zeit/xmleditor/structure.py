# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import gocept.lxml.interfaces

import zope.component
import zope.interface

import zeit.cms.content.property
import zeit.xmleditor.interfaces


@zope.interface.implementer(zeit.xmleditor.interfaces.IEditableStructure)
@zope.component.adapter(gocept.lxml.interfaces.IObjectified)
def structureFactory(element):
    return zope.component.getAdapter(
        element,
        zeit.xmleditor.interfaces.IEditableStructure,
        name=element.tag)


class StructureBase(object):

    zope.component.adapts(gocept.lxml.interfaces.IObjectified)

    def __init__(self, element):
        self.xml = element


class XInclude(StructureBase):

    zope.interface.implements(zeit.xmleditor.interfaces.IXInclude)

    href = zeit.cms.content.property.ObjectPathAttributeProperty(None, 'href')
    fallback = zeit.cms.content.property.ObjectPathProperty(
        '.{http://www.w3.org/2001/XInclude}fallback')


class Block(StructureBase):

    zope.interface.implements(zeit.xmleditor.interfaces.IBlock)

    priority = zeit.cms.content.property.ObjectPathAttributeProperty(
        None, 'priority', zeit.xmleditor.interfaces.IBlock['priority'])
    layout = zeit.cms.content.property.ObjectPathAttributeProperty(
        None, 'layout')
    id = zeit.cms.content.property.ObjectPathAttributeProperty(
        None, 'id')
    href = zeit.cms.content.property.ObjectPathAttributeProperty(
        None, 'href')


class Text(StructureBase):

    zope.interface.implements(zeit.xmleditor.interfaces.IText)

    text = zeit.cms.content.property.ObjectPathProperty(None)


class Raw(StructureBase):

    zope.interface.implements(zeit.xmleditor.interfaces.IRaw)
