# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import UserDict
import gocept.lxml.interfaces
import itertools
import rwproperty
import uuid
import zeit.content.cp.block
import zeit.content.cp.interfaces
import zope.component
import zope.container.contained
import zope.event
import zope.interface


class Area(UserDict.DictMixin,
           zope.container.contained.Contained):

    def __init__(self, context, xml):
        self.__parent__ = context
        self.xml = xml

    def __repr__(self):
        return '<%s.%s for %s>' % (self.__module__, self.__class__.__name__,
                                   self.xml.get('area'))
    @property
    def __name__(self):
        return self.xml.get('area')

    def __getitem__(self, key):
        # XXX this is not very efficient
        for node in self.xml.iterchildren():
            if node.get('{http://namespaces.zeit.de/CMS/cp}__name__') != key:
                continue
            block_type = node.get('{http://namespaces.zeit.de/CMS/cp}type')
            block = zope.component.getMultiAdapter(
                (self, node),
                zeit.content.cp.interfaces.IBlock,
                name=block_type)
            return zope.container.contained.contained(block, self, key)
        raise KeyError(key)

    def __iter__(self):
        for node in self.xml.iterchildren():
            key = node.get('{http://namespaces.zeit.de/CMS/cp}__name__')
            if key is not None:
                yield key

    def keys(self):
        return list(self.__iter__())

    def add(self, item):
        name = self._add(item)
        zope.event.notify(zope.container.contained.ObjectAddedEvent(
            item, self, name))

    def _add(self, item):
        name = item.__name__
        if name:
            if name in self:
                raise zope.container.interfaces.DuplicateIDError(name)
        else:
            name = str(uuid.uuid4())
        item.__name__ = name
        self.xml.append(item.xml)
        return name

    def updateOrder(self, order):
        if not isinstance(order, (tuple, list)):
            raise TypeError('order must be tuple or list, got %s.' %
                            type(order))
        if set(order) != set(self.keys()):
            raise ValueError('order must have the same keys.')
        objs = dict(self.items())
        for key in order:
            self._delete(key)
        for key in order:
            self._add(objs[key])
        zope.event.notify(
            zope.container.contained.ContainerModifiedEvent(self))

    def __delitem__(self, key):
        item = self._delete(key)
        zope.event.notify(
            zope.container.contained.ObjectRemovedEvent(item, self, key))

    def _delete(self, key):
        item = self[key]
        item.xml.getparent().remove(item.xml)
        return item


@zope.component.adapter(zeit.content.cp.interfaces.IArea)
@zope.interface.implementer(zeit.content.cp.interfaces.ICMSContentIterable)
def cms_content_iter(context):
    return itertools.chain(*[
        zeit.content.cp.interfaces.ICMSContentIterable(block)
        for block in context.values()])


class Region(Area):

    zope.interface.implements(zeit.content.cp.interfaces.IRegion)
    zope.component.adapts(
        zeit.content.cp.interfaces.ICenterPage,
        gocept.lxml.interfaces.IObjectified)


class LeadRegion(Region):

    zope.interface.implements(zeit.content.cp.interfaces.ILeadRegion)


class Cluster(Area):

    zope.interface.implements(zeit.content.cp.interfaces.ICluster)
    zope.component.adapts(
        zeit.content.cp.interfaces.ICenterPage,
        gocept.lxml.interfaces.IObjectified)


@zope.interface.implementer(zeit.content.cp.interfaces.ICenterPage)
@zope.component.adapter(zeit.content.cp.interfaces.IArea)
def area_to_centerpage(context):
    return zeit.content.cp.interfaces.ICenterPage(context.__parent__)



class TeaserBar(zeit.content.cp.block.Block, Area):

    zope.interface.implements(zeit.content.cp.interfaces.ITeaserBar)

    def __init__(self, context, xml):
        super(TeaserBar, self).__init__(context, xml)
        self.placeholder_factory = zope.component.getAdapter(
            self, zeit.content.cp.interfaces.IBlockFactory, name='placeholder')

    @rwproperty.getproperty
    def layout(self):
        for layout in zeit.content.cp.interfaces.ITeaserBar['layout'].source:
            if layout.id == self.xml.get('module'):
                return layout

    @rwproperty.setproperty
    def layout(self, layout):
        content_blocks = len(
            [x for x in self.values()
             if not zeit.content.cp.interfaces.IPlaceHolder.providedBy(x)])
        if content_blocks > layout.blocks:
            raise ValueError(
                "Cannot change layout to '%s': allows only %s blocks,"
                " but have %s content blocks already"
                % (layout.id, layout.blocks, content_blocks))

        self.xml.set('module', layout.id)

        if len(self) < layout.blocks:
            for x in range(layout.blocks - len(self)):
                self.placeholder_factory()

        for key, block in reversed(self.items()):
            if len(self) == layout.blocks:
                break
            if zeit.content.cp.interfaces.IPlaceHolder.providedBy(block):
                del self[key]

    def __repr__(self):
        return object.__repr__(self)


class TeaserBarFactory(zeit.content.cp.block.BlockFactory):

    zope.component.adapts(zeit.content.cp.interfaces.ICluster)

    block_class = TeaserBar
    block_type = 'teaser-bar'
    title = None

    def get_xml(self):
        region = super(TeaserBarFactory, self).get_xml()
        region.tag = 'region'
        region.set('area', 'teaser-row-full')
        return region

    def __call__(self):
        bar = super(TeaserBarFactory, self).__call__()
        # Prepopulate with placeholders
        factory = zope.component.getAdapter(
            bar, zeit.content.cp.interfaces.IBlockFactory, name='placeholder')
        for x in range(4):
            factory()
        return bar
