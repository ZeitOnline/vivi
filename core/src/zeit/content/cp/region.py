# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.lxml.interfaces
import uuid
import zeit.cms.content.interfaces
import zeit.content.cp.interfaces
import zope.component
import zope.dottedname.resolve
import zope.interface


class Region(object):

    zope.interface.implements(zeit.content.cp.interfaces.IEditableArea)

    zope.component.adapts(
        zeit.content.cp.interfaces.ICenterPage,
        gocept.lxml.interfaces.IObjectified)

    def __init__(self, context, xml):
        self.context = context
        self.xml = xml

    def __getitem__(self, key):
        # XXX this is not very efficient
        for node in self.xml.iterchildren():
            if node.get('{http://namespaces.zeit.de/CMS/cp}__name__') != key:
                continue
            class_name = node.get(
                '{http://namespaces.zeit.de/CMS/cp}class', 'teaser')
            class_ = zope.dottedname.resolve.resolve(class_name)
            return class_(self, node)
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
