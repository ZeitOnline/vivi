# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.lxml.interfaces
import zeit.cms.content.interfaces
import zeit.content.cp.interfaces
import zope.component
import zope.interface


class Region(object):

    zope.interface.implements(zeit.content.cp.interfaces.IEditableArea)

    zope.component.adapts(
        zeit.content.cp.interfaces.ICenterPage,
        gocept.lxml.interfaces.IObjectified)

    def __init__(self, context, xml):
        self.context = context
        self.xml = xml

    def __repr__(self):
        return '<%s.%s for %s>' % (self.__module__, self.__class__.__name__,
                                   self.xml.get('area'))
