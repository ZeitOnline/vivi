# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import StringIO
import mock
import unittest


class RuleTest(unittest.TestCase):

    def apply_rule(self, rule):
        from zeit.edit.rule import Rule
        r = Rule(rule)
        with mock.patch('zeit.edit.interfaces.IRuleGlobs') as irg:
            irg.return_value = {}
            return r.apply(mock.Mock)

    def test_not_applicable_should_raise(self):
        s = self.apply_rule("""
applicable(False)
invalid_name
""")
        self.assertEquals(None, s.status)

    def test_valid_rule_should_return_none(self):
        s = self.apply_rule("applicable(True)")
        self.assertEquals(None, s.status)

    def test_invalid_rule_should_return_code(self):
        import zeit.edit.rule
        s = self.apply_rule("error_if(True)")
        self.assertEquals(zeit.edit.rule.ERROR, s.status)
        s = self.apply_rule("error_unless(False)")
        self.assertEquals(zeit.edit.rule.ERROR, s.status)

    def test_warning_with_message(self):
        import zeit.edit.rule
        s = self.apply_rule('warning_unless(False, "A dire warning")')
        self.assertEquals(zeit.edit.rule.WARNING, s.status)
        self.assertEquals('A dire warning', s.message)
        s = self.apply_rule("warning_if(True)")
        self.assertEquals(zeit.edit.rule.WARNING, s.status)

    def test_error_overrides_warning(self):
        import zeit.edit.rule
        s = self.apply_rule("""
error_if(True, "An error message")
warning_if(True, "A warning")
""")
        self.assertEquals(zeit.edit.rule.ERROR, s.status)
        self.assertEquals('An error message', s.message)


class RulesManagerTest(unittest.TestCase):

    def get_processed_rules(self, rules):
        import gocept.cache.method
        import zeit.edit.rule
        rm = zeit.edit.rule.RulesManager()
        gocept.cache.method.clear()
        with mock.patch('zope.app.appsetup.product.getProductConfiguration') \
                as gpc:
            gpc.return_value = {'rules-url': mock.sentinel.rulesurl}
            with mock.patch('urllib2.urlopen') as urlopen:
                urlopen.return_value = StringIO.StringIO(rules)
                return rm.rules

    def test_valid_rules_file_should_be_loaded(self):
        rules = self.get_processed_rules("""\
applicable(False)
error_if(False)

applicable(True)

applicable(True)
                                         """)
        self.assertEqual(3, len(rules))

    def test_invalid_rules_file_should_yield_empty_ruleset(self):
        rules = self.get_processed_rules("if 1=2")
        self.assertEqual(0, len(rules))
