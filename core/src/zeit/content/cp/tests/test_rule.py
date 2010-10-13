# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from __future__ import with_statement
from zeit.content.cp.rule import Rule
import gocept.cache
import pkg_resources
import unittest
import zeit.cms.interfaces
import zeit.cms.workflow.interfaces
import zeit.content.cp.centerpage
import zeit.content.cp.testing
import zeit.edit.interfaces
import zope.app.appsetup.product
import zope.component


class RuleTest(zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        super(RuleTest, self).setUp()
        self.cp = zeit.content.cp.centerpage.CenterPage()
        factory = zope.component.getAdapter(
            self.cp['lead'], zeit.edit.interfaces.IElementFactory,
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
            zeit.edit.interfaces.IElementFactory,
            name='teaser-bar')
        bar = factory()
        factory = zope.component.getAdapter(
            bar, zeit.edit.interfaces.IElementFactory,
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
            zeit.edit.interfaces.IElementFactory,
            name='teaser-bar')
        bar = factory()
        r = Rule("""
applicable(is_region and area == 'teaser-mosaic' and position)
error_if(True, u'Region in teasermosaic.')
""")
        s = r.apply(bar)
        self.assertEquals(zeit.content.cp.rule.ERROR, s.status)

    def test_teaserbar_is_no_block(self):
        factory = zope.component.getAdapter(
            self.cp['teaser-mosaic'],
            zeit.edit.interfaces.IElementFactory,
            name='teaser-bar')
        bar = factory()
        r = Rule("""
applicable(is_block and area == 'teaser-mosaic')
error_if(True)
""")
        s = r.apply(bar)
        self.assertNotEquals(zeit.content.cp.rule.ERROR, s.status)

    def test_content_glob(self):
        r = Rule("""
applicable(is_block and content)
error_if(True)
""")
        s = r.apply(self.teaser)
        self.assertNotEquals(zeit.content.cp.rule.ERROR, s.status)
        self.teaser.insert(0, zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/testcontent'))
        s = r.apply(self.teaser)
        self.assertEquals(zeit.content.cp.rule.ERROR, s.status)

    def test_content_glob_is_empty_for_non_content_blocks(self):
        r = Rule("""
applicable(is_block)
error_unless(content == [])
""")
        factory = zope.component.getAdapter(
            self.cp['informatives'],
            zeit.edit.interfaces.IElementFactory,
            name='xml')
        s = r.apply(factory())
        self.assertNotEquals(zeit.content.cp.rule.ERROR, s.status)

    def test_published_glob(self):
        r = Rule("""
applicable(is_block and content)
error_unless(is_published(content[0]))
""")
        tc = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/testcontent')
        self.teaser.insert(0, tc)
        s = r.apply(self.teaser)
        self.assertEquals(zeit.content.cp.rule.ERROR, s.status)
        zeit.cms.workflow.interfaces.IPublishInfo(tc).published = True
        s = r.apply(self.teaser)
        self.assertNotEquals(zeit.content.cp.rule.ERROR, s.status)

    def test_cp_type_glob(self):
        r = Rule("""
applicable(cp_type == 'homepage')
error_if(True)
""")
        s = r.apply(self.teaser)
        self.assertNotEquals(zeit.content.cp.rule.ERROR, s.status)
        self.cp.type = u'homepage'
        s = r.apply(self.teaser)
        self.assertEquals(zeit.content.cp.rule.ERROR, s.status)

    def test_globs_should_never_return_none(self):
        del self.teaser.xml.attrib['{http://namespaces.zeit.de/CMS/cp}type']

        r = Rule("""
applicable(type != 'teaser')
error_if(True, type)
""")
        s = r.apply(self.teaser)
        self.assertEquals(zeit.content.cp.rule.ERROR, s.status)
        self.assertEquals('__NONE__', s.message)


class RulesManagerTest(zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        super(RulesManagerTest, self).setUp()
        self.rm = zope.component.getUtility(
            zeit.content.cp.interfaces.IRulesManager)

    def tearDown(self):
        self._set_rules('example_rules.py')
        super(RulesManagerTest, self).tearDown()

    def _set_rules(self, filename):
        zope.app.appsetup.product._configs['zeit.content.cp']['rules-url'] = (
            'file://' + pkg_resources.resource_filename(
                'zeit.content.cp.tests.fixtures', filename))
        gocept.cache.method.clear()
        self.rm._rules[:] = []

    def test_valid_rules_file_should_be_loaded(self):
        self._set_rules('example_rules.py')
        self.assertEqual(3, len(self.rm.rules))

    def test_invalid_rules_file_should_yield_empty_ruleset(self):
        self._set_rules('syntax_error')
        self.assertEqual(0, len(self.rm.rules))
