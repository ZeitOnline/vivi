# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.i18n import MessageFactory as _
import zeit.cms.content.property
import zeit.cms.content.xmlsupport
import zeit.cms.content.xmlsupport
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zope.component
import zope.interface

class FullGraphicalBlock(zeit.content.cp.blocks.block.Block):

    zope.interface.implements(zeit.content.cp.interfaces.IFullGraphicalBlock)

    referenced_object = zeit.cms.content.property.SingleResource(
        '.block', xml_reference_name='related', attributes=('href',))

    image = zeit.cms.content.property.SingleResource(
        '.image', xml_reference_name='related', attributes=('href',))

FullGraphicalFactory = zeit.content.cp.blocks.block.blockFactoryFactory(
    zeit.content.cp.interfaces.IRegion, 'fullgraphicalblock',
    _('Fullgraphical Block'))
