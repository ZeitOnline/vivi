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

    def setUp(self):
        import gocept.cache.method
        gocept.cache.method.clear()

    def get_manager(self):
        import zeit.edit.rule
        return zeit.edit.rule.RulesManager()

    def get_processed_rules(self, rules):
        rm = self.get_manager()
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

    def test_unset_product_config_should_not_fail(self):
        rm = self.get_manager()
        with mock.patch('zope.app.appsetup.product.getProductConfiguration') \
                as gpc:
            gpc.return_value = None
            self.assertEqual([], rm.get_rules())

    def test_unset_url_should_not_fail(self):
        rm = self.get_manager()
        with mock.patch('zope.app.appsetup.product.getProductConfiguration') \
                as gpc:
            gpc.return_value = {'foo': 'bar'}
            self.assertEqual([], rm.get_rules())


class RecursiveValidatorTest(unittest.TestCase):

    def setUp(self):
        import zeit.edit.interfaces
        import zope.component

        self.validator = mock.Mock()
        self.validator().status = None
        self.validator().messages = []
        self.validator.reset_mock()
        zope.component.provideAdapter(
            self.validator,
            adapts=(mock.Mock,),
            provides=zeit.edit.interfaces.IValidator)

    def test_should_call_validator_for_all_children(self):
        from zeit.edit.rule import RecursiveValidator
        m1 = mock.Mock()
        m2 = mock.Mock()
        RecursiveValidator([m1, m2])
        self.assertEqual(
            [((m1,), {}), ((m2,), {})], self.validator.call_args_list)

    def test_should_accumulate_messages(self):
        from zeit.edit.rule import RecursiveValidator
        self.validator().messages = [mock.sentinel.message]
        validator = RecursiveValidator([mock.Mock(), mock.Mock()])
        self.assertEqual(
            [mock.sentinel.message, mock.sentinel.message], validator.messages)

    def test_error_overrides_warning(self):
        from zeit.edit.rule import RecursiveValidator, ERROR, WARNING

        v1 = mock.Mock()
        v1.status = ERROR
        v1.messages = []
        v2 = mock.Mock()
        v2.status = WARNING
        v2.messages = []
        results = [v1, v2]
        self.validator.side_effect = lambda x: results.pop()

        validator = RecursiveValidator([mock.Mock(), mock.Mock()])
        self.assertEqual(ERROR, validator.status)
