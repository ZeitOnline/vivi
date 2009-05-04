# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.interfaces import ITeaserBlock, IPlaceHolder
from zeit.content.cp.layout import get_layout
import lxml.objectify
import unittest
import zeit.cms.testing
import zeit.content.cp.area
import zeit.content.cp.tests
import zope.component


class TeaserBarTest(zeit.cms.testing.FunctionalTestCase):
    layer = zeit.content.cp.tests.layer

    def setUp(self):
        super(TeaserBarTest, self).setUp()
        cp = zeit.content.cp.centerpage.CenterPage()
        self.bar = zeit.content.cp.area.TeaserBar(cp['teaser-mosaic'],
                                                  lxml.objectify.E.region())
        self.bar.layout = get_layout('normal')

    def item(self, index):
        return self.bar[self.bar.keys()[index]]

    def test_normal_layout_has_four_placeholders(self):
        self.assertEquals(4, len(self.bar))

    def test_change_layout_to_normal(self):
        self.bar.layout = get_layout('normal')
        self.assertEquals(4, len(self.bar))

    def test_change_layout_to_advertisement(self):
        self.bar.layout = get_layout('dmr')
        self.assertEquals(2, len(self.bar))

    def test_non_placeholder_blocks_are_preserved(self):
        bar = self.bar
        del bar[bar.keys()[0]]
        teaser_factory = zope.component.getAdapter(
            bar, zeit.content.cp.interfaces.IBlockFactory, name='teaser')
        teaser_factory()

        # 0=placeholder, x=teaser
        # [0, 0, 0, x]
        bar.layout = get_layout('dmr')
        self.assertEquals(2, len(bar))
        # expect: [0, x]
        self.assert_(IPlaceHolder.providedBy(self.item(0)))
        self.assert_(ITeaserBlock.providedBy(self.item(1)))

        teaser_factory()
        teaser_factory()
        # [0, x, x, x]
        bar.layout = get_layout('dmr')
        # we delete as much placeholders as we can
        self.assertEquals(3, len(bar))

    def test_placeholders_intermixed_are_deleted(self):
        bar = self.bar
        for key in bar:
            del bar[key]
        teaser_factory = zope.component.getAdapter(
            bar, zeit.content.cp.interfaces.IBlockFactory, name='teaser')
        placeholder_factory = zope.component.getAdapter(
            bar, zeit.content.cp.interfaces.IBlockFactory, name='placeholder')
        placeholder_factory()
        teaser_factory()
        placeholder_factory()
        teaser_factory()
        # [0, x, 0, x]

        bar.layout = get_layout('mr')
        # expect: [0, x, x]
        self.assert_(IPlaceHolder.providedBy(self.item(0)))
        self.assert_(ITeaserBlock.providedBy(self.item(1)))
        self.assert_(ITeaserBlock.providedBy(self.item(2)))

        bar.layout = get_layout('dmr')
        # expect: [x, x]
        self.assert_(ITeaserBlock.providedBy(self.item(0)))
        self.assert_(ITeaserBlock.providedBy(self.item(1)))


def test_suite():
    return unittest.makeSuite(TeaserBarTest)
