# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import UserDict
import gocept.lxml.interfaces
import itertools
import lxml.etree
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zope.component
import zeit.edit.container
import zope.interface


class Container(zeit.edit.container.Base):

    def _find_item(self, xml_node, name):
        nodes = lxml.etree.XPath(
            './*[@cms:__name__ = $name]',
            namespaces=dict(
                cms='http://namespaces.zeit.de/CMS/cp'))
        if nodes:
            return nodes[0]

    _get_keys = lxml.etree.XPath(
        './*/attribute::cms:__name__',
        namespaces=dict(
            cms='http://namespaces.zeit.de/CMS/cp'))

    def _get_element_type(self, xml_node):
          return xml_node.get('{http://namespaces.zeit.de/CMS/cp}type')


@zope.component.adapter(zeit.edit.interfaces.IArea)
@zope.interface.implementer(zeit.content.cp.interfaces.ICMSContentIterable)
def cms_content_iter(context):
    return itertools.chain(*[
        zeit.content.cp.interfaces.ICMSContentIterable(block)
        for block in context.values()
        if block is not None])


class Region(Container):

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


class Mosaic(Container):

    zope.interface.implements(zeit.content.cp.interfaces.IMosaic,
                              zeit.edit.interfaces.IArea)
    zope.component.adapts(
        zeit.content.cp.interfaces.ICenterPage,
        gocept.lxml.interfaces.IObjectified)

    __name__ = 'teaser-mosaic'


@zope.interface.implementer(zeit.content.cp.interfaces.ICenterPage)
@zope.component.adapter(zeit.edit.interfaces.IContainer)
def container_to_centerpage(context):
    return zeit.content.cp.interfaces.ICenterPage(context.__parent__)
