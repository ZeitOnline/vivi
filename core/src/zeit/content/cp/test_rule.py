# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.rule import Rule
import unittest
import zeit.cms.testing
import zeit.content.cp.centerpage
import zeit.content.cp.tests
import zope.component


class RuleTest(zeit.cms.testing.FunctionalTestCase):
    layer = zeit.content.cp.tests.layer

    def setUp(self):
        super(RuleTest, self).setUp()
        self.cp = zeit.content.cp.centerpage.CenterPage()
        factory = zope.component.getAdapter(
            self.cp['lead'], zeit.content.cp.interfaces.IBlockFactory,
            name='teaser')
        self.teaser = factory()

    def test_not_applicable_should_raise(self):
        r = Rule("""
                 applicable(False)
                 invalid_name
                 """)
        self.assertEquals(None, r.apply(self.teaser))

    def test_valid_rule_should_return_none(self):
        r = Rule("""
                 applicable(True)
                 """)
        self.assertEquals(None, r.apply(self.teaser))

    def test_invalid_rule_should_return_code(self):
        r = Rule("""
                 error_if(True)
                 """)
        self.assertEquals(zeit.content.cp.rule.ERROR, r.apply(self.teaser))

        r = Rule("""
                 error_unless(False)
                 """)
        self.assertEquals(zeit.content.cp.rule.ERROR, r.apply(self.teaser))

    def test_warning_with_message(self):
        r = Rule("""
                 warning_unless(False, "A dire warning")
                 """)
        self.assertEquals(zeit.content.cp.rule.WARNING, r.apply(self.teaser))
        self.assertEquals('A dire warning', r.message)

        r = Rule("""
                 warning_if(True)
                 """)
        self.assertEquals(zeit.content.cp.rule.WARNING, r.apply(self.teaser))

    def test_error_overrides_warning(self):
        r = Rule("""
                 error_if(True, "An error message")
                 warning_if(True, "A warning")
                 """)
        self.assertEquals(zeit.content.cp.rule.ERROR, r.apply(self.teaser))
        self.assertEquals('An error message', r.message)

    def test_block_rule(self):
        r = Rule("""
                 warning_if(is_block)
                 error_if(is_area)
                 """)
        self.assertEquals(zeit.content.cp.rule.WARNING, r.apply(self.teaser))

    def test_area_rule(self):
        r = Rule("""
                 warning_if(is_block)
                 error_if(is_area)
                 """)
        self.assertEquals(zeit.content.cp.rule.ERROR, r.apply(self.cp['lead']))

def test_suite():
    return unittest.makeSuite(RuleTest)
