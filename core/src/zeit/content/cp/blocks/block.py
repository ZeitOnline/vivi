# Copyright (c) 2009-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.content.property
import zeit.content.cp.interfaces
import zeit.edit.block
import zeit.edit.interfaces
import zope.component
import zope.interface


@zope.interface.implementer(zeit.content.cp.interfaces.ICenterPage)
@zope.component.adapter(zeit.edit.interfaces.IElement)
def cms_content_to_centerpage(context):
    return zeit.content.cp.interfaces.ICenterPage(context.__parent__, None)


@zope.component.adapter(zeit.edit.interfaces.IElement)
@zope.interface.implementer(zeit.content.cp.interfaces.ICMSContentIterable)
def cms_content_iter(context):
    return iter([])


class Block(zeit.edit.block.Element):

    title = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'title')

    publisher = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'publisher')
    publisher_url = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'publisher_url')

    supertitle = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'supertitle')
    supertitle_url = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'supertitle_url')

    read_more = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'read_more')
    read_more_url = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'read_more_url')
