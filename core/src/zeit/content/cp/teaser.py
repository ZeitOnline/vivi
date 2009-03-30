# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import lxml.objectify
import zeit.content.cp.interfaces
import zope.component
import zope.interface
from zeit.content.cp.i18n import MessageFactory as _


class TeaserListFactory(object):

    zope.interface.implements(zeit.content.cp.interfaces.IModuleFactory)
    zope.component.adapts(zeit.content.cp.interfaces.IEditableArea)

    title = _('List of teasers')

    def __init__(self, context):
        self.context = context

    def __call__(self):
        container = lxml.objectify.E.container()
        tl = TeaserList(self.context, container)
        self.context.add(tl)
        return tl


class TeaserList(object):

    def __init__(self, context, xml):
        self.context = context
        self.xml = xml
        self.xml.set(
            '{http://namespaces.zeit.de/CMS/cp}class',
            '%s.%s' % (self.__class__.__module__, self.__class__.__name__))

    @property
    def __name__(self):
        return self.xml.get('{http://namespaces.zeit.de/CMS/cp}__name__')
