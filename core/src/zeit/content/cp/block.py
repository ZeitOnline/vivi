# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.lxml.interfaces
import lxml.objectify
import zeit.content.cp.interfaces
import zope.component
import zope.interface


class BlockFactory(object):
    """Base class for block factories."""

    zope.interface.implements(zeit.content.cp.interfaces.IBlockFactory)

    def __init__(self, context):
        self.context = context

    def get_xml(self):
        container = lxml.objectify.E.container()
        container.set('{http://namespaces.zeit.de/CMS/cp}type', self.block_type)
        return container

    def __call__(self):
        container = self.get_xml()
        block = self.block_class(self.context, container)
        self.context.add(block)
        return block


def blockFactoryFactory(adapts, block_class, block_type, title=None):
    """A factory which creates a block factory."""
    class_name = '%sFactory' % block_type.capitalize()
    factory = type(class_name, (BlockFactory,), dict(
        title=title,
        block_class=block_class,
        block_type=block_type))
    factory = zope.component.adapter(adapts)(factory)
    return factory


@zope.interface.implementer(zeit.content.cp.interfaces.ICenterPage)
@zope.component.adapter(zeit.content.cp.interfaces.IBlock)
def block_to_centerpage(context):
    return zeit.content.cp.interfaces.ICenterPage(context.__parent__)


class Block(zope.container.contained.Contained):
    """Base class for blocks."""

    zope.component.adapts(
        zeit.content.cp.interfaces.IArea,
        gocept.lxml.interfaces.IObjectified)

    title = zeit.cms.content.property.ObjectPathProperty('.title')

    def __init__(self, context, xml):
        self.__parent__ = context
        self.xml = xml

    def _get_name(self):
        return self.xml.get('{http://namespaces.zeit.de/CMS/cp}__name__')

    def _set_name(self, name):
        return self.xml.set('{http://namespaces.zeit.de/CMS/cp}__name__', name)

    __name__ = property(_get_name, _set_name)

    @property
    def type(self):
        return self.xml.get('{http://namespaces.zeit.de/CMS/cp}type')


class PlaceHolder(Block):

    zope.interface.implements(zeit.content.cp.interfaces.IPlaceHolder)


PlaceHolderFactory = blockFactoryFactory(
    zeit.content.cp.interfaces.IRegion,
    PlaceHolder, 'placeholder')
