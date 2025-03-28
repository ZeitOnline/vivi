from io import StringIO
from unittest import mock
import unittest

import lxml.etree
import pendulum
import zope.component
import zope.interface

from zeit.cms.workflow.interfaces import CAN_PUBLISH_ERROR
import zeit.cms.testcontenttype.interfaces
import zeit.cms.workflow.interfaces
import zeit.edit.interfaces
import zeit.edit.rule
import zeit.edit.testing
import zeit.workflow.browser.publish


class RuleTest(unittest.TestCase):
    def apply_rule(self, rule):
        from zeit.edit.rule import Rule

        r = Rule(rule)
        return r.apply(mock.Mock, {})

    def test_not_applicable_should_raise(self):
        s = self.apply_rule(
            """
applicable(False)
invalid_name
"""
        )
        self.assertEqual(None, s.status)

    def test_valid_rule_should_return_none(self):
        s = self.apply_rule('applicable(True)')
        self.assertEqual(None, s.status)

    def test_invalid_rule_should_return_code(self):
        import zeit.edit.rule

        s = self.apply_rule('error_if(True)')
        self.assertEqual(zeit.edit.rule.ERROR, s.status)
        s = self.apply_rule('error_unless(False)')
        self.assertEqual(zeit.edit.rule.ERROR, s.status)

    def test_warning_with_message(self):
        import zeit.edit.rule

        s = self.apply_rule('warning_unless(False, "A dire warning")')
        self.assertEqual(zeit.edit.rule.WARNING, s.status)
        self.assertEqual('A dire warning', s.message)
        s = self.apply_rule('warning_if(True)')
        self.assertEqual(zeit.edit.rule.WARNING, s.status)

    def test_error_overrides_warning(self):
        import zeit.edit.rule

        s = self.apply_rule(
            """
error_if(True, "An error message")
warning_if(True, "A warning")
"""
        )
        self.assertEqual(zeit.edit.rule.ERROR, s.status)
        self.assertEqual('An error message', s.message)


class GlobTest(zeit.edit.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()

        import zeit.edit.block
        import zeit.edit.container

        self.xml = lxml.etree.fromstring(
            """
<body xmlns:cms="http://namespaces.zeit.de/CMS/cp">
  <p cms:type="foo">Para1</p>
</body>
"""
        )

        Area = type('DummyArea', (dict,), {})
        page = Area()
        page.__parent__ = None
        self.area = Area()
        self.area.__name__ = 'testarea'
        self.area.__parent__ = page
        self.area.type = 'area'
        page['testarea'] = self.area
        zope.interface.alsoProvides(self.area, zeit.edit.interfaces.IArea)
        self.block = zeit.edit.block.SimpleElement(self.area, self.xml.find('p'))
        self.block.__name__ = 'bar'
        self.area['bar'] = self.block

    def apply(self, rule, context):
        return rule.apply(context, zeit.edit.interfaces.IRuleGlobs(context))

    def test_type(self):
        import zeit.edit.rule

        r = zeit.edit.rule.Rule(
            """
warning_if(type == 'foo')
error_if(True)
"""
        )
        s = self.apply(r, self.block)
        self.assertEqual(zeit.edit.rule.ERROR, s.status)

    def test_is_block(self):
        import zeit.edit.rule

        r = zeit.edit.rule.Rule(
            """
error_if(is_block)
"""
        )
        s = self.apply(r, self.block)
        self.assertEqual(None, s.status)

        zope.interface.alsoProvides(self.block, zeit.edit.interfaces.IBlock)
        s = self.apply(r, self.block)
        self.assertEqual(zeit.edit.rule.ERROR, s.status)

    def test_is_area(self):
        import zeit.edit.rule

        r = zeit.edit.rule.Rule(
            """
error_if(is_area)
"""
        )
        s = self.apply(r, self.block)
        self.assertEqual(None, s.status)

        s = self.apply(r, self.area)
        self.assertEqual(zeit.edit.rule.ERROR, s.status)

    def test_area(self):
        pass

    def test_count(self):
        pass

    def test_position(self):
        pass

    def test_is_published(self):
        import zeit.cms.interfaces
        import zeit.edit.rule

        r = zeit.edit.rule.Rule(
            """
error_unless(is_published(context))
"""
        )
        tc = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/testcontent')
        s = self.apply(r, tc)
        self.assertEqual(zeit.edit.rule.ERROR, s.status)
        zeit.cms.workflow.interfaces.IPublishInfo(tc).published = True
        r.status = None
        s = self.apply(r, tc)
        self.assertNotEqual(zeit.edit.rule.ERROR, s.status)

    def test_scheduled_for_publishing(self):
        import zeit.cms.interfaces
        import zeit.edit.rule
        import zeit.workflow.workflow

        class Timebased(zeit.workflow.timebased.TimeBasedWorkflow):
            def log(self, *args, **kw):
                pass

        zope.component.getSiteManager().registerAdapter(
            Timebased, provided=zeit.cms.workflow.interfaces.IPublishInfo
        )

        r = zeit.edit.rule.Rule(
            """
error_unless(scheduled_for_publishing(context))
"""
        )
        tc = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/testcontent')
        zope.interface.alsoProvides(tc, zeit.cms.interfaces.IEditorialContent)
        s = self.apply(r, tc)
        self.assertEqual(zeit.edit.rule.ERROR, s.status)

        now = pendulum.now('UTC')
        pi = zeit.cms.workflow.interfaces.IPublishInfo(tc)
        pi.release_period = (now, None)
        r.status = None
        s = self.apply(r, tc)
        self.assertNotEqual(zeit.edit.rule.ERROR, s.status)

        pi.release_period = (now, now.add(days=1))
        r.status = None
        s = self.apply(r, tc)
        self.assertNotEqual(zeit.edit.rule.ERROR, s.status)

    def test_globs_should_never_return_none(self):
        import zeit.edit.rule

        r = zeit.edit.rule.Rule(
            """
applicable(type != 'foo')
error_if(True, type)
"""
        )
        del self.block.xml.attrib['{http://namespaces.zeit.de/CMS/cp}type']
        s = self.apply(r, self.block)
        self.assertEqual(zeit.edit.rule.ERROR, s.status)
        self.assertEqual('__NONE__', s.message)


class RulesManagerTest(zeit.edit.testing.FunctionalTestCase):
    def setUp(self):
        import pyramid_dogpile_cache2

        super().setUp()
        pyramid_dogpile_cache2.clear()

    def get_manager(self):
        import zeit.edit.rule

        return zeit.edit.rule.RulesManager()

    def get_processed_rules(self, rules):
        rm = self.get_manager()
        with mock.patch('zope.app.appsetup.product.getProductConfiguration') as gpc:
            gpc.return_value = {'rules-url': mock.sentinel.rulesurl}
            with mock.patch('zeit.cms.content.sources.load') as load:
                load.return_value = StringIO(rules)
                return rm.rules

    def test_valid_rules_file_should_be_loaded(self):
        rules = self.get_processed_rules(
            """\
applicable(False)
error_if(False)

applicable(True)

applicable(True)
                                         """
        )
        self.assertEqual(3, len(rules))

    def test_invalid_rules_file_should_yield_empty_ruleset(self):
        rules = self.get_processed_rules('if 1=2')
        self.assertEqual(0, len(rules))
        rules = self.get_processed_rules('')
        self.assertEqual(0, len(rules))


class RecursiveValidatorTest(unittest.TestCase):
    def setUp(self):
        import zope.component

        import zeit.edit.interfaces

        self.validator = mock.Mock()
        self.validator().status = None
        self.validator().messages = []
        self.validator.reset_mock()
        zope.component.provideAdapter(
            self.validator, adapts=(mock.Mock,), provides=zeit.edit.interfaces.IValidator
        )

    def test_should_call_validator_for_all_children(self):
        from zeit.edit.rule import RecursiveValidator

        m1 = mock.Mock()
        m2 = mock.Mock()
        RecursiveValidator([m1, m2])
        self.assertEqual([((m1,), {}), ((m2,), {})], self.validator.call_args_list)

    def test_should_accumulate_messages(self):
        from zeit.edit.rule import RecursiveValidator

        self.validator().messages = [mock.sentinel.message]
        validator = RecursiveValidator([mock.Mock(), mock.Mock()])
        self.assertEqual([mock.sentinel.message, mock.sentinel.message], validator.messages)

    def test_error_overrides_warning(self):
        from zeit.edit.rule import ERROR, WARNING, RecursiveValidator

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


@zope.component.adapter(zeit.cms.testcontenttype.interfaces.IExampleContentType)
@zope.interface.implementer(zeit.cms.workflow.interfaces.IPublishInfo)
def validating_workflow_for_testcontent(context):
    return zeit.edit.rule.ValidatingWorkflow(context)


@zope.component.adapter(zeit.cms.testcontenttype.interfaces.IExampleContentType)
@zope.interface.implementer(zeit.edit.interfaces.IValidator)
def validator_for_testcontent(context):
    validator = mock.Mock(status=zeit.edit.rule.ERROR, messages=['Mock Validator Error Message'])
    return validator


class ValidatingWorkflowTest(zeit.edit.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        gsm = zope.component.getGlobalSiteManager()
        gsm.registerAdapter(validating_workflow_for_testcontent)
        gsm.registerAdapter(validator_for_testcontent)

    def tearDown(self):
        super().tearDown()
        gsm = zope.component.getGlobalSiteManager()
        gsm.unregisterAdapter(validating_workflow_for_testcontent)
        gsm.unregisterAdapter(validator_for_testcontent)

    def test_validating_workflow_cannot_publish_when_validation_failed(self):
        workflow = zeit.cms.workflow.interfaces.IPublishInfo(self.repository['testcontent'])
        self.assertEqual(CAN_PUBLISH_ERROR, workflow.can_publish())

    def test_validating_workflow_provides_error_messages_for_publish_info(self):
        view = zeit.workflow.browser.publish.Publish()
        view.context = self.repository['testcontent']
        view.can_publish()
        self.assertEqual('Mock Validator Error Message', view.error_messages[1])
