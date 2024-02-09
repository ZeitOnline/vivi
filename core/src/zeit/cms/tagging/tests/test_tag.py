# coding: utf-8
from unittest import mock
import unittest

import lxml.etree
import zope.component

from zeit.cms.checkout.helper import checked_out
import zeit.cms.interfaces
import zeit.cms.tagging.interfaces
import zeit.cms.tagging.tag
import zeit.cms.tagging.testing
import zeit.cms.testing
import zeit.retresco.testing


class TestTags(unittest.TestCase, zeit.cms.tagging.testing.TaggingHelper):
    def get_content(self):
        from zeit.cms.tagging.tag import Tags

        class Content:
            tags = Tags()

        return Content()

    def test_get_without_tagger_should_be_empty(self):
        self.assertEqual((), self.get_content().tags)

    def test_set_should_raise_without_tagger(self):
        def set():
            self.get_content().tags = ()

        self.assertRaises(TypeError, lambda: set())

    def test_get_should_return_tagger_values(self):
        t1 = mock.Mock()
        t2 = mock.Mock()
        t1.disabled = False
        t2.disabled = False
        with mock.patch('zeit.cms.tagging.interfaces.ITagger') as tagger:
            tagger().values.return_value = [t1, t2]
            result = self.get_content().tags
        self.assertEqual((t1, t2), result)
        tagger().values.assert_called_with()

    def test_set_should_add_new_values_to_tagger(self):
        tags = self.setup_tags('t1', 't2')
        t1 = tags['t1']
        t2 = tags['t2']
        del tags['t2']
        self.get_content().tags = [t1, t2]
        result = self.get_content().tags
        self.assertEqual(['t1', 't2'], [x.label for x in result])

    def test_set_should_remove_remaining_values_from_tagger(self):
        tags = self.setup_tags('t1', 't2')
        self.get_content().tags = [tags['t1']]
        result = self.get_content().tags
        self.assertEqual(['t1'], [x.label for x in result])

    def test_set_should_update_pinned_tags(self):
        tags = self.setup_tags('t1', 't2')
        t1 = tags['t1']
        t1.pinned = True
        with mock.patch.object(tags, 'set_pinned') as set_pinned:
            self.get_content().tags = [t1, tags['t2']]
            set_pinned.assert_called_with([t1.code])

    def test_set_should_add_duplicate_values_only_once(self):
        tags = self.setup_tags('t1', 't2')
        t1 = tags['t1']
        self.get_content().tags = [t1, t1]
        result = self.get_content().tags
        self.assertEqual(['t1'], [x.label for x in result])


class TestCMSContentWiring(
    zeit.cms.testing.ZeitCmsBrowserTestCase, zeit.cms.tagging.testing.TaggingHelper
):
    # This test checks that the Tag object and its views etc are wired up
    # properly so that they can be addressed as ICMSContent and traversed to.
    # We need these things so we can use the ObjectSequenceWidget to edit tags.

    def test_object_details(self):
        self.setup_tags('foo')
        base = 'http://localhost/++skin++vivi/'
        browser = self.browser
        browser.open('{}@@redirect_to?unique_id=tag://foo&view=@@object-details'.format(base))

        self.assertEqual('<h3>foo (Test)</h3>', browser.contents)

    def test_redirecting_to_tag_with_unicode_escaped_url_yields_tag(self):
        # Redirect tests IAbsoluteURL and Traverser, so we know it's symmetric.
        self.setup_tags('Bärlin')
        code = 'Bärlin'.encode('unicode_escape').decode('ascii')
        base = 'http://localhost/++skin++vivi/'
        browser = self.browser
        browser.open('{}@@redirect_to?unique_id=tag://{}&view=@@object-details'.format(base, code))
        self.assertEqual('<h3>Bärlin (Test)</h3>', browser.contents)

    def test_adapting_tag_url_to_cmscontent_yields_a_copy(self):
        from zeit.cms.interfaces import ICMSContent

        self.setup_tags('foo')
        t1 = ICMSContent('tag://foo')
        t2 = ICMSContent('tag://foo')
        t1.pinned = True
        self.assertFalse(t2.pinned)

    def test_adapting_tag_url_with_escaped_unicode_yields_tag(self):
        from zeit.cms.interfaces import ICMSContent

        self.setup_tags('Bärlin')
        tag = ICMSContent('tag://%s' % 'Bärlin'.encode('unicode_escape').decode('ascii'))
        self.assertEqual('Bärlin', tag.label)

    def test_adapting_unicode_escaped_uniqueId_of_tag_yields_tag(self):
        from zeit.cms.interfaces import ICMSContent

        self.setup_tags('Bärlin')
        whitelist = zope.component.queryUtility(zeit.cms.tagging.interfaces.IWhitelist)
        tag = ICMSContent(whitelist.get('Bärlin').uniqueId)
        self.assertEqual('Bärlin', tag.label)


class TestSyncToXML(
    zeit.cms.testing.ZeitCmsBrowserTestCase, zeit.cms.tagging.testing.TaggingHelper
):
    def test_copies_tags_to_head(self):
        self.setup_tags('foo')
        with checked_out(self.repository['testcontent']):
            pass
        self.assertEllipsis(
            '...<tag...>foo</tag>...',
            lxml.etree.tostring(self.repository['testcontent'].xml.find('head'), encoding=str),
        )

    def test_leaves_xml_without_head_alone(self):
        content = self.repository['testcontent']
        content.xml.remove(content.xml.find('head'))
        self.setup_tags('foo')
        with self.assertNothingRaised():
            # Need to fake checkin, since other handlers re-create the <head>.
            zeit.cms.tagging.tag.add_ranked_tags_to_head(content)


class TagTest(zeit.retresco.testing.FunctionalTestCase):
    """Testing ..tag.Tag."""

    def test_from_code_generates_a_tag_object_equal_to_its_source(self):
        tag = zeit.cms.tagging.tag.Tag('Vipraschül', 'Person')
        self.assertEqual(tag, zeit.cms.tagging.tag.Tag.from_code(tag.code))

    def test_uniqueId_from_tag_can_be_adapted_to_tag(self):
        tag = zeit.cms.tagging.tag.Tag('Vipraschül', 'Person')
        self.assertEqual(tag, zeit.cms.interfaces.ICMSContent(tag.uniqueId))

    def test_comparison_to_object_that_is_no_tag_returns_False(self):
        tag = zeit.cms.tagging.tag.Tag('Vipraschül', 'Person')
        self.assertEqual(False, tag == {})

    def test_not_equal_comparison_is_supported(self):
        tag = zeit.cms.tagging.tag.Tag('Vipraschül', 'Person')
        self.assertEqual(False, tag != zeit.cms.tagging.tag.Tag('Vipraschül', 'Person'))
        self.assertEqual(True, tag != {})

    def test_from_code_returns_None_if_invalid_code_given(self):
        self.assertEqual(None, zeit.cms.tagging.tag.Tag.from_code('invalid-code'))
