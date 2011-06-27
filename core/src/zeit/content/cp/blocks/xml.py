# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.i18n import MessageFactory as _
import lxml.objectify
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.edit.block
import zope.container.interfaces
import zope.interface


class XMLBlock(zeit.content.cp.blocks.block.Block):

    zope.interface.implements(
        zeit.content.cp.interfaces.IXMLBlock,
        zope.container.interfaces.IContained)


class XMLBlockFactory(zeit.edit.block.TypeOnAttributeElementFactory):

    zope.component.adapts(zeit.content.cp.interfaces.IRegion)
    element_type = module = 'xml'
    title = _('Raw XML block')

    def get_xml(self):
        container = super(XMLBlockFactory, self).get_xml()
        raw = lxml.objectify.E.raw(u'\n\n\n')
        lxml.objectify.deannotate(raw)
        container.append(raw)
        return container
