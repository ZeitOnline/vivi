# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest2 as unittest
import zeit.cms.testing
import zope.component
import zope.security.management
import zope.testbrowser.testing


class TestTags(unittest.TestCase,
               zeit.cms.tagging.testing.TaggingHelper):

    def get_content(self):
        from zeit.cms.tagging.tag import Tags

        class Content(object):
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
        self.assertEqual(['t1', 't2'], [x.code for x in result])

    def test_set_should_remove_remaining_values_from_tagger(self):
        tags = self.setup_tags('t1', 't2')
        self.get_content().tags = [tags['t1']]
        result = self.get_content().tags
        self.assertEqual(['t1'], [x.code for x in result])

    def test_set_should_update_pinned_tags(self):
        tags = self.setup_tags('t1', 't2')
        t1 = tags['t1']
        t1.pinned = True
        with mock.patch.object(tags, 'set_pinned') as set_pinned:
            self.get_content().tags = [t1, tags['t2']]
            set_pinned.assert_called_with(['t1'])

    def test_set_should_add_duplicate_values_only_once(self):
        tags = self.setup_tags('t1', 't2')
        t1 = tags['t1']
        self.get_content().tags = [t1, t1]
        result = self.get_content().tags
        self.assertEqual(['t1'], [x.code for x in result])


class TestCMSContentWiring(zeit.cms.testing.BrowserTestCase):

    # This test checks that the Tag object and its views etc are wired up
    # properly so that they can be addressed as ICMSContent and traversed to.
    # We need these things so we can use the ObjectSequenceWidget to edit tags.

    def test_object_details(self):
        from zeit.cms.tagging.tag import Tag

        whitelist = zope.component.getUtility(
            zeit.cms.tagging.interfaces.IWhitelist)
        whitelist['foo'] = Tag('foo', 'foo')

        base = 'http://localhost/++skin++vivi/'
        b = self.browser
        b.open(
            base + '@@redirect_to?unique_id=tag://foo&view=@@object-details')
        self.assertEqual('<h3>foo</h3>', b.contents)

    def test_adapting_tag_url_to_cmscontent_yields_a_copy(self):
        from zeit.cms.interfaces import ICMSContent
        from zeit.cms.tagging.tag import Tag
        whitelist = zope.component.getUtility(
            zeit.cms.tagging.interfaces.IWhitelist)
        whitelist['foo'] = Tag('foo', 'foo')
        t1 = ICMSContent('tag://foo')
        t2 = ICMSContent('tag://foo')
        t1.pinned = True
        self.assertFalse(t2.pinned)
