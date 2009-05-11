# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp.blocks.block
import zope.interface
import zeit.content.cp.interfaces



class PlaceHolder(zeit.content.cp.blocks.block.Block):

    zope.interface.implements(zeit.content.cp.interfaces.IPlaceHolder)


PlaceHolderFactory = zeit.content.cp.blocks.block.blockFactoryFactory(
    zeit.content.cp.interfaces.IRegion,
    PlaceHolder, 'placeholder')
