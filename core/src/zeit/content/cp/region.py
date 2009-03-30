# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.lxml.interfaces
import uuid
import zeit.cms.content.interfaces
import zeit.content.cp.interfaces
import zope.component
import zope.container.contained
import zope.dottedname.resolve
import zope.interface


class Region(zope.container.contained.Contained):

    zope.interface.implements(zeit.content.cp.interfaces.IRegion)

    zope.component.adapts(
        zeit.content.cp.interfaces.ICenterPage,
        gocept.lxml.interfaces.IObjectified)

    def __init__(self, context, xml):
        self.__parent__ = context
        self.xml = xml

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
                yield self[key]

    def add(self, item):
        name = item.xml.get('{http://namespaces.zeit.de/CMS/cp}__name__')
        if name is not None:
            raise this_is_not_tested_yet
        name = str(uuid.uuid4())
        item.xml.set('{http://namespaces.zeit.de/CMS/cp}__name__', name)
        self.xml.append(item.xml)

    def __repr__(self):
        return '<%s.%s for %s>' % (self.__module__, self.__class__.__name__,
                                   self.xml.get('area'))


@zope.interface.implementer(zeit.content.cp.interfaces.ICenterPage)
@zope.component.adapter(zeit.content.cp.interfaces.IArea)
def area_to_centerpage(context):
    return zeit.content.cp.interfaces.ICenterPage(context.__parent__)
