# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.interfaces import IAutoPilotTeaserBlock
from zeit.content.cp.layout import get_bar_layout
import lxml.objectify
import unittest
import zeit.content.cp.blocks.teaserbar
import zeit.content.cp.testing
import zeit.edit.interfaces
import zope.component


class TeaserBarTest(zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        super(TeaserBarTest, self).setUp()
        cp = zeit.content.cp.centerpage.CenterPage()
        self.bar = zeit.content.cp.blocks.teaserbar.TeaserBar(cp['teaser-mosaic'],
                                                  lxml.objectify.E.region())
        self.bar.layout = get_bar_layout('normal')

    def item(self, index):
        return self.bar[self.bar.keys()[index]]

    def test_normal_layout_has_four_placeholders(self):
        self.assertEquals(4, len(self.bar))

    def test_change_layout_to_normal(self):
        self.bar.layout = get_bar_layout('normal')
        self.assertEquals(4, len(self.bar))

    def test_change_layout_to_advertisement(self):
        self.bar.layout = get_bar_layout('dmr')
        self.assertEquals(1, len(self.bar))

    def test_non_placeholder_blocks_are_preserved(self):
        bar = self.bar
        del bar[bar.keys()[0]]
        teaser_factory = zope.component.getAdapter(
            bar, zeit.edit.interfaces.IElementFactory, name='teaser')
        teaser_factory()

        # 0=placeholder, x=teaser
        # [0, 0, 0, x]
        bar.layout = get_bar_layout('dmr')
        self.assertEquals(1, len(bar))
        # expect: [x]
        self.assert_(IAutoPilotTeaserBlock.providedBy(self.item(0)))

        teaser_factory()
        teaser_factory()
        # [x, x, x]
        bar.layout = get_bar_layout('dmr')
        # we delete as much placeholders as we can
        self.assertEquals(3, len(bar))

    def test_placeholders_intermixed_are_deleted(self):
        bar = self.bar
        for key in bar:
            del bar[key]
        teaser_factory = zope.component.getAdapter(
            bar, zeit.edit.interfaces.IElementFactory, name='teaser')
        placeholder_factory = zope.component.getAdapter(
            bar, zeit.edit.interfaces.IElementFactory, name='placeholder')
        placeholder_factory()
        teaser_factory()
        placeholder_factory()
        teaser_factory()
        # [0, x, 0, x]

        bar.layout = get_bar_layout('mr')
        # expect: [x, x]
        self.assert_(IAutoPilotTeaserBlock.providedBy(self.item(0)))
        self.assert_(IAutoPilotTeaserBlock.providedBy(self.item(1)))

        bar.layout = get_bar_layout('dmr')
        # expect: [x, x]
        self.assert_(IAutoPilotTeaserBlock.providedBy(self.item(0)))
        self.assert_(IAutoPilotTeaserBlock.providedBy(self.item(1)))


def test_suite():
    return unittest.makeSuite(TeaserBarTest)
