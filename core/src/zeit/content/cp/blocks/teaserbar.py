# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp.area
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.content.cp.layout
import zope.component
import zope.interface


class TeaserBar(zeit.content.cp.area.Container):

    zope.interface.implements(zeit.content.cp.interfaces.ITeaserBar)

    @property
    def placeholder_factory(self):
        return zope.component.getAdapter(
            self, zeit.content.cp.interfaces.IElementFactory,
            name='placeholder')

    @property
    def layout(self):
        for layout in zeit.content.cp.interfaces.ITeaserBar['layout'].source(self):
            if layout.id == self.xml.get('module'):
                return layout
        return zeit.content.cp.interfaces.IReadTeaserBar['layout'].default

    @layout.setter
    def layout(self, layout):
        self._p_changed = True
        self.xml.set('module', layout.id)

        if len(self) < layout.blocks:
            for x in range(layout.blocks - len(self)):
                self.placeholder_factory()

        for key, block in reversed(self.items()):
            if len(self) == layout.blocks:
                break
            if zeit.content.cp.interfaces.IPlaceHolder.providedBy(block):
                del self[key]

    def __repr__(self):
        return object.__repr__(self)


class TeaserBarFactory(zeit.content.cp.blocks.block.ElementFactory):

    zope.component.adapts(zeit.content.cp.interfaces.IMosaic)

    element_class = TeaserBar
    element_type = 'teaser-bar'
    title = None
    module = zeit.content.cp.interfaces.IReadTeaserBar[
            'layout'].default.id

    def get_xml(self):
        region = super(TeaserBarFactory, self).get_xml()
        region.tag = 'region'
        region.set('area', 'teaser-row-full')
        return region

    def __call__(self):
        bar = super(TeaserBarFactory, self).__call__()
        # Prepopulate with placeholders
        factory = zope.component.getAdapter(
            bar, zeit.content.cp.interfaces.IElementFactory, name='placeholder')
        for x in range(zeit.content.cp.layout.MAX_TEASER_BAR_BLOCKS):
            factory()
        return bar
