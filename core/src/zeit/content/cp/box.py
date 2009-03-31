# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.lxml.interfaces
import lxml.objectify
import zeit.content.cp.interfaces
import zope.component
import zope.interface


class BoxFactory(object):
    """Base class for box factories."""

    zope.interface.implements(zeit.content.cp.interfaces.IBoxFactory)

    def __init__(self, context):
        self.context = context

    def get_xml(self):
        container = lxml.objectify.E.container()
        container.set('{http://namespaces.zeit.de/CMS/cp}type', self.box_type)
        return container

    def __call__(self):
        container = self.get_xml()
        box = self.box_class(self.context, container)
        self.context.add(box)
        return box


def boxFactoryFactory(adapts, box_class, box_type, title=None):
    """A factory which creates a box factory."""
    class_name = '%sFactory' % box_type.capitalize()
    factory = type(class_name, (BoxFactory,), dict(
        title=title,
        box_class=box_class,
        box_type=box_type))
    factory = zope.component.adapter(adapts)(factory)
    return factory


@zope.interface.implementer(zeit.content.cp.interfaces.ICenterPage)
@zope.component.adapter(zeit.content.cp.interfaces.IBox)
def box_to_centerpage(context):
    return zeit.content.cp.interfaces.ICenterPage(context.__parent__)


class Box(zope.container.contained.Contained):
    """Base class for boxes."""

    zope.component.adapts(
        zeit.content.cp.interfaces.IArea,
        gocept.lxml.interfaces.IObjectified)

    title = zeit.cms.content.property.ObjectPathProperty('.title')

    def __init__(self, context, xml):
        self.__parent__ = context
        self.xml = xml

    @property
    def __name__(self):
        return self.xml.get('{http://namespaces.zeit.de/CMS/cp}__name__')

    @property
    def type(self):
        return self.xml.get('{http://namespaces.zeit.de/CMS/cp}type')


class PlaceHolder(Box):

    zope.interface.implements(zeit.content.cp.interfaces.IPlaceHolder)


PlaceHolderFactory = boxFactoryFactory(
    zeit.content.cp.interfaces.IRegion,
    PlaceHolder, 'placeholder')
