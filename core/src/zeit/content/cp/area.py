# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.lxml.interfaces
import grokcore.component as grok
import itertools
import lxml
import zeit.content.cp.interfaces
import zeit.edit.container
import zope.component
import zope.interface


@zope.component.adapter(zeit.edit.interfaces.IArea)
@zope.interface.implementer(zeit.content.cp.interfaces.ICMSContentIterable)
def cms_content_iter(context):
    return itertools.chain(*[
        zeit.content.cp.interfaces.ICMSContentIterable(block)
        for block in context.values()
        if block is not None])


class Region(zeit.edit.container.TypeOnAttributeContainer):

    zope.interface.implements(zeit.content.cp.interfaces.IRegion)
    zope.component.adapts(
        zeit.content.cp.interfaces.ICenterPage,
        gocept.lxml.interfaces.IObjectified)


class Lead(Region):

    zope.interface.implements(zeit.content.cp.interfaces.ILead,
                              zeit.edit.interfaces.IArea)

    __name__ = 'lead'


class Informatives(Region):

    zope.interface.implements(zeit.content.cp.interfaces.IInformatives,
                              zeit.edit.interfaces.IArea)

    __name__ = 'informatives'


class Mosaic(zeit.edit.container.TypeOnAttributeContainer):

    zope.interface.implements(zeit.content.cp.interfaces.IMosaic,
                              zeit.edit.interfaces.IArea)
    zope.component.adapts(
        zeit.content.cp.interfaces.ICenterPage,
        gocept.lxml.interfaces.IObjectified)

    __name__ = 'teaser-mosaic'


@zope.interface.implementer(zeit.content.cp.interfaces.ICenterPage)
@zope.component.adapter(zeit.edit.interfaces.IContainer)
def container_to_centerpage(context):
    # Is this required? Is there any IContainer which is not an IElement at the
    # same time?
    return zeit.content.cp.interfaces.ICenterPage(context.__parent__, None)


@grok.adapter(zeit.content.cp.interfaces.IRegion)
@grok.implementer(zeit.content.cp.interfaces.IRenderedXML)
def rendered_xml(context):
    region = getattr(lxml.objectify.E, context.xml.tag)(**context.xml.attrib)
    region.attrib.pop('automatic', None)
    # XXX This API is non-obvious: IAutomaticRegion also works for regions
    # that are not or can never be automatic.
    for block in zeit.content.cp.interfaces.IAutomaticRegion(context).values():
        region.append(zeit.content.cp.interfaces.IRenderedXML(block))
    return region


@grok.adapter(zeit.content.cp.interfaces.IMosaic)
@grok.implementer(zeit.content.cp.interfaces.IRenderedXML)
def rendered_xml_mosaic(context):
    root = getattr(lxml.objectify.E, context.xml.tag)(**context.xml.attrib)
    for item in context.values():
        root.append(zeit.content.cp.interfaces.IRenderedXML(item))
    return root
