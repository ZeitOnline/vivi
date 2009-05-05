# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.rule import Rule
import unittest
import zeit.cms.testing
import zeit.content.cp.centerpage
import zeit.content.cp.tests


class RuleTest(zeit.cms.testing.FunctionalTestCase):
    layer = zeit.content.cp.tests.layer

    def setUp(self):
        super(RuleTest, self).setUp()

    def test_not_applicable_should_raise(self):
        r = Rule("""
                 applicable(False)
                 invalid_name
                 """)
        self.assertEquals(None, r.apply(None))

    def test_valid_rule_should_return_none(self):
        r = Rule("""
                 applicable(True)
                 """)
        self.assertEquals(None, r.apply(None))

    def test_invalid_rule_should_return_code(self):
        r = Rule("""
                 error_if(True)
                 """)
        self.assertEquals(zeit.content.cp.rule.ERROR, r.apply(None))

        r = Rule("""
                 error_unless(False)
                 """)
        self.assertEquals(zeit.content.cp.rule.ERROR, r.apply(None))

    def test_message_is_stored(self):
        r = Rule("""
                 message("My test error message")
                 """)
        r.apply(None)
        self.assertEquals('My test error message', r.message)

    def test_warning_with_message(self):
        r = Rule("""
                 message("A dire warning")
                 warning_unless(False)
                 """)
        self.assertEquals(zeit.content.cp.rule.WARNING, r.apply(None))
        self.assertEquals('A dire warning', r.message)

        r = Rule("""
                 warning_if(True)
                 """)
        self.assertEquals(zeit.content.cp.rule.WARNING, r.apply(None))


def test_suite():
    return unittest.makeSuite(RuleTest)
