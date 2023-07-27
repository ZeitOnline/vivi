from zeit.edit.interfaces import IRuleGlobs
from zeit.edit.rule import Rule
import importlib.resources
import pyramid_dogpile_cache2
import zeit.cms.interfaces
import zeit.content.cp.centerpage
import zeit.content.cp.testing
import zeit.edit.interfaces
import zeit.edit.rule
import zope.app.appsetup.product
import zope.component


class RuleTest(zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        super().setUp()
        self.cp = zeit.content.cp.centerpage.CenterPage()
        self.teaser = self.cp['lead'].create_item('teaser')

    def test_content_glob(self):
        r = Rule("""
applicable(is_block and content)
error_if(True)
""")
        s = r.apply(self.teaser, IRuleGlobs(self.teaser))
        self.assertNotEqual(zeit.edit.rule.ERROR, s.status)
        self.teaser.insert(0, zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/testcontent'))
        s = r.apply(self.teaser, IRuleGlobs(self.teaser))
        self.assertEqual(zeit.edit.rule.ERROR, s.status)

    def test_content_glob_is_empty_for_non_content_blocks(self):
        r = Rule("""
applicable(is_block)
error_unless(content == [])
""")
        area = self.cp['informatives'].create_item('xml')
        s = r.apply(area, IRuleGlobs(area))
        self.assertNotEqual(zeit.edit.rule.ERROR, s.status)

    def test_cp_type_glob(self):
        r = Rule("""
applicable(cp_type == 'homepage')
error_if(True)
""")
        s = r.apply(self.teaser, IRuleGlobs(self.teaser))
        self.assertNotEqual(zeit.edit.rule.ERROR, s.status)
        self.cp.type = 'homepage'
        s = r.apply(self.teaser, IRuleGlobs(self.teaser))
        self.assertEqual(zeit.edit.rule.ERROR, s.status)

    def test_feature_is_a_region(self):
        r = Rule("""
applicable(is_region)
error_if(True)
""")
        s = r.apply(self.cp['feature'], IRuleGlobs(self.cp['feature']))
        self.assertEqual(zeit.edit.rule.ERROR, s.status)

    def test_area_is_not_a_region(self):
        area = self.cp['feature'].create_item('area')
        r = Rule("""
applicable(is_region)
error_if(True)
""")
        s = r.apply(area, IRuleGlobs(area))
        self.assertNotEqual(zeit.edit.rule.ERROR, s.status)

    def test_centerpage_glob(self):
        r = Rule("""
applicable(is_block)
error_if(centerpage.title == 'foo')
""")
        s = r.apply(self.teaser, IRuleGlobs(self.teaser))
        self.assertNotEqual(zeit.edit.rule.ERROR, s.status)
        self.cp.title = 'foo'
        s = r.apply(self.teaser, IRuleGlobs(self.teaser))
        self.assertEqual(zeit.edit.rule.ERROR, s.status)

    def test_all_modules_glob(self):
        r = Rule("""
applicable(is_block)
error_if(len(list(all_modules)) == 2)
""")
        s = r.apply(self.teaser, IRuleGlobs(self.teaser))
        self.assertNotEqual(zeit.edit.rule.ERROR, s.status)
        self.cp['lead'].create_item('teaser')
        s = r.apply(self.teaser, IRuleGlobs(self.teaser))
        self.assertEqual(zeit.edit.rule.ERROR, s.status)


class RulesManagerTest(zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        import zeit.edit.interfaces
        super().setUp()
        self.rm = zope.component.getUtility(
            zeit.edit.interfaces.IRulesManager)

    def _set_rules(self, filename):
        zope.app.appsetup.product._configs['zeit.edit']['rules-url'] = (
            'file://%s' % (importlib.resources.files(
                __package__) / 'fixtures' / filename))
        pyramid_dogpile_cache2.clear()
        self.rm._rules[:] = []

    def test_valid_rules_file_should_be_loaded(self):
        self._set_rules('example_rules.py')
        self.assertEqual(2, len(self.rm.rules))

    def test_invalid_rules_file_should_yield_empty_ruleset(self):
        self._set_rules('syntax_error')
        self.assertEqual(0, len(self.rm.rules))
