# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.interface

import zeit.cms.content.property
import zeit.xmleditor.structure

import zeit.content.centerpage.interfaces


class Container(zeit.xmleditor.structure.StructureBase):

    zope.interface.implements(zeit.content.centerpage.interfaces.IContainer)

    label = zeit.cms.content.property.ObjectPathAttributeProperty(
        None, 'label')
    style = zeit.cms.content.property.ObjectPathAttributeProperty(
        None, 'style')
    layout = zeit.cms.content.property.ObjectPathAttributeProperty(
        None, 'layout')


class Column(zeit.xmleditor.structure.StructureBase):

    zope.interface.implements(zeit.content.centerpage.interfaces.IColumn)

    layout = zeit.cms.content.property.ObjectPathAttributeProperty(
        None, 'layout')
