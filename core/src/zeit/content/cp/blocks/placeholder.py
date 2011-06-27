# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp.blocks.block
import zope.interface
import zeit.content.cp.interfaces


class PlaceHolder(zeit.content.cp.blocks.block.Block):

    zope.interface.implements(zeit.content.cp.interfaces.IPlaceHolder)


zeit.edit.block.register_element_factory(
    [zeit.content.cp.interfaces.IInformatives,
     zeit.content.cp.interfaces.ITeaserBar], 'placeholder')
