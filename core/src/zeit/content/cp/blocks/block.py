# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.lxml.interfaces
import lxml.objectify
import zeit.cms.content.property
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
        if getattr(self, 'module', None):
            container.set('module', self.module)
        return container

    def __call__(self):
        container = self.get_xml()
        block = zope.component.getMultiAdapter(
            (self.context, container),
            zeit.content.cp.interfaces.IBlock,
            name=self.block_type)
        self.context.add(block)
        return block


def blockFactoryFactory(adapts, block_type, title=None, module=None):
    """A factory which creates a block factory."""
    class_name = '%sFactory' % block_type.capitalize()
    factory = type(class_name, (BlockFactory,), dict(
        title=title,
        block_type=block_type,
        module=module))
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


@zope.component.adapter(zeit.content.cp.interfaces.IBlock)
@zope.interface.implementer(zeit.content.cp.interfaces.ICMSContentIterable)
def cms_content_iter(context):
    return iter([])
