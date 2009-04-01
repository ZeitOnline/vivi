# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import UserDict
import gocept.lxml.interfaces
import uuid
import zeit.cms.content.interfaces
import zeit.content.cp.box
import zeit.content.cp.interfaces
import zope.component
import zope.container.contained
import zope.dottedname.resolve
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
            box_type = node.get('{http://namespaces.zeit.de/CMS/cp}type')
            box = zope.component.getMultiAdapter(
                (self, node),
                zeit.content.cp.interfaces.IBox,
                name=box_type)
            return zope.container.contained.contained(box, self, key)
        raise KeyError(key)

    def __iter__(self):
        for node in self.xml.iterchildren():
            key = node.get('{http://namespaces.zeit.de/CMS/cp}__name__')
            if key is not None:
                yield key

    def keys(self):
        return list(self.__iter__())

    def add(self, item):
        name = item.xml.get('{http://namespaces.zeit.de/CMS/cp}__name__')
        if name is not None:
            raise NotImplementedError
        name = str(uuid.uuid4())
        item.xml.set('{http://namespaces.zeit.de/CMS/cp}__name__', name)
        self.xml.append(item.xml)
        zope.event.notify(zope.container.contained.ObjectAddedEvent(
            item, self, name))

    def __delitem__(self, key):
        box = self[key]
        box.xml.getparent().remove(box.xml)


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



class TeaserBar(zeit.content.cp.box.Box, Area):

    zope.interface.implements(zeit.content.cp.interfaces.ITeaserBar)

    def __repr__(self):
        return object.__repr__(self)


class TeaserBarFactory(zeit.content.cp.box.BoxFactory):

    zope.component.adapts(zeit.content.cp.interfaces.ICluster)

    box_class = TeaserBar
    box_type = 'teaser-bar'
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
            bar, zeit.content.cp.interfaces.IBoxFactory, name='placeholder')
        for x in range(4):
            factory()
        return bar
