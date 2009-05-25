# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.rule import Rule
import unittest
import zeit.content.cp.centerpage
import zeit.content.cp.testing
import zope.component


class RuleTest(zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        super(RuleTest, self).setUp()
        self.cp = zeit.content.cp.centerpage.CenterPage()
        factory = zope.component.getAdapter(
            self.cp['lead'], zeit.content.cp.interfaces.IElementFactory,
            name='teaser')
        self.teaser = factory()

    def test_not_applicable_should_raise(self):
        r = Rule("""
applicable(False)
invalid_name
""")
        s = r.apply(self.teaser)
        self.assertEquals(None, s.status)

    def test_valid_rule_should_return_none(self):
        r = Rule("""
applicable(True)
""")
        s = r.apply(self.teaser)
        self.assertEquals(None, s.status)

    def test_invalid_rule_should_return_code(self):
        r = Rule("""
error_if(True)
""")
        s = r.apply(self.teaser)
        self.assertEquals(
            zeit.content.cp.rule.ERROR, s.status)

        r = Rule("""
error_unless(False)
""")
        s = r.apply(self.teaser)
        self.assertEquals(zeit.content.cp.rule.ERROR, s.status)

    def test_warning_with_message(self):
        r = Rule("""
warning_unless(False, "A dire warning")
""")
        s = r.apply(self.teaser)
        self.assertEquals(zeit.content.cp.rule.WARNING, s.status)
        self.assertEquals('A dire warning', s.message)

        r = Rule("""
warning_if(True)
""")
        s = r.apply(self.teaser)
        self.assertEquals(zeit.content.cp.rule.WARNING, s.status)

    def test_error_overrides_warning(self):
        r = Rule("""
error_if(True, "An error message")
warning_if(True, "A warning")
""")
        s = r.apply(self.teaser)
        self.assertEquals(zeit.content.cp.rule.ERROR, s.status)
        self.assertEquals('An error message', s.message)

    def test_is_block(self):
        r = Rule("""
warning_if(is_block)
error_if(is_area)
""")
        s = r.apply(self.teaser)
        self.assertEquals(zeit.content.cp.rule.WARNING, s.status)

    def test_is_area(self):
        r = Rule("""
warning_if(is_block)
error_if(is_area)
""")
        s = r.apply(self.cp['lead'])
        self.assertEquals(zeit.content.cp.rule.ERROR, s.status)

    def test_is_block_in_teasermosaic_should_apply_to_block(self):
        factory = zope.component.getAdapter(
            self.cp['teaser-mosaic'],
            zeit.content.cp.interfaces.IElementFactory,
            name='teaser-bar')
        bar = factory()
        factory = zope.component.getAdapter(
            bar, zeit.content.cp.interfaces.IElementFactory,
            name='teaser')
        teaser = factory()
        r = Rule("""
applicable(is_block and area == 'teaser-mosaic')
error_if(True, u'Block in teasermosaic.')
""")
        s = r.apply(teaser)
        self.assertEquals(zeit.content.cp.rule.ERROR, s.status)

    def test_is_region_in_teasermosaic_should_apply_to_teaserbar(self):
        factory = zope.component.getAdapter(
            self.cp['teaser-mosaic'],
            zeit.content.cp.interfaces.IElementFactory,
            name='teaser-bar')
        bar = factory()
        r = Rule("""
applicable(is_region and area == 'teaser-mosaic' and position)
error_if(True, u'Region in teasermosaic.')
""")
        s = r.apply(bar)
        self.assertEquals(zeit.content.cp.rule.ERROR, s.status)

    def test_is_tesaerbar_is_no_block(self):
        factory = zope.component.getAdapter(
            self.cp['teaser-mosaic'],
            zeit.content.cp.interfaces.IElementFactory,
            name='teaser-bar')
        bar = factory()
        r = Rule("""
applicable(is_block and area == 'teaser-mosaic')
error_if(True)
""")
        s = r.apply(bar)
        self.assertNotEquals(zeit.content.cp.rule.ERROR, s.status)


def test_suite():
    return unittest.makeSuite(RuleTest)
