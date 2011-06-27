# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import UserDict
import gocept.lxml.interfaces
import itertools
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zope.component
import zeit.edit.container
import zope.interface


@zope.component.adapter(zeit.edit.interfaces.IArea)
@zope.interface.implementer(zeit.content.cp.interfaces.ICMSContentIterable)
def cms_content_iter(context):
    return itertools.chain(*[
        zeit.content.cp.interfaces.ICMSContentIterable(block)
        for block in context.values()
        if block is not None])


class Region(zeit.edit.container.TypeOnAttributeContainer):

    zope.interface.implements(zeit.content.cp.interfaces.IRegion)
    zope.component.adapts(
        zeit.content.cp.interfaces.ICenterPage,
        gocept.lxml.interfaces.IObjectified)


class Lead(Region):

    zope.interface.implements(zeit.content.cp.interfaces.ILead,
                              zeit.edit.interfaces.IArea)

    __name__ = 'lead'


class Informatives(Region):

    zope.interface.implements(zeit.content.cp.interfaces.IInformatives,
                              zeit.edit.interfaces.IArea)

    __name__ = 'informatives'


class Mosaic(zeit.edit.container.TypeOnAttributeContainer):

    zope.interface.implements(zeit.content.cp.interfaces.IMosaic,
                              zeit.edit.interfaces.IArea)
    zope.component.adapts(
        zeit.content.cp.interfaces.ICenterPage,
        gocept.lxml.interfaces.IObjectified)

    __name__ = 'teaser-mosaic'


@zope.interface.implementer(zeit.content.cp.interfaces.ICenterPage)
@zope.component.adapter(zeit.edit.interfaces.IContainer)
def container_to_centerpage(context):
    # Is this required? Is there any IContainer which is not an IElement at the
    # same time?
    return zeit.content.cp.interfaces.ICenterPage(context.__parent__, None)
