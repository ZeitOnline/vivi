# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.lxml.interfaces
import lxml.objectify
import zeit.content.cp.interfaces
import zope.component
import zope.container.contained
import zope.interface
from zeit.content.cp.i18n import MessageFactory as _


class TeaserListFactory(object):

    zope.interface.implements(zeit.content.cp.interfaces.IBoxFactory)
    zope.component.adapts(zeit.content.cp.interfaces.IRegion)

    title = _('List of teasers')

    def __init__(self, context):
        self.context = context

    def __call__(self):
        container = lxml.objectify.E.container()
        container.set('{http://namespaces.zeit.de/CMS/cp}type', 'teaser')
        tl = TeaserList(self.context, container)
        self.context.add(tl)
        return tl


class TeaserList(zope.container.contained.Contained):

    zope.interface.implements(zeit.content.cp.interfaces.ITeaserList)
    zope.component.adapts(
        zeit.content.cp.interfaces.IRegion,
        gocept.lxml.interfaces.IObjectified)

    def __init__(self, context, xml):
        self.__parent__ = context
        self.xml = xml

    @property
    def __name__(self):
        return self.xml.get('{http://namespaces.zeit.de/CMS/cp}__name__')
