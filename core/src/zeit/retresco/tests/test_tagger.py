# coding: utf8
from unittest import mock
from zeit.cms.checkout.helper import checked_out
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.cms.tagging.tag import Tag
from zeit.retresco.tagger import Tagger
from zeit.retresco.testing import create_testcontent
import lxml.objectify
import six
import unittest
import zeit.cms.content.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.tagging.interfaces
import zeit.connector.interfaces
import zeit.retresco.testing
import zope.component
import zope.interface
import zope.lifecycleevent

try:
    import zeit.intrafind.tag
    import zeit.intrafind.tagger
    HAVE_INTRAFIND = True
except ImportError:  # Soft dependency, only needed for transitional period
    HAVE_INTRAFIND = False


class TestTagger(zeit.retresco.testing.FunctionalTestCase,
                 zeit.retresco.testing.TagTestHelpers):

    def test_tagger_should_provide_interface(self):
        self.repository['content'] = ExampleContentType()
        self.assertTrue(
            zope.interface.verify.verifyObject(
                zeit.cms.tagging.interfaces.ITagger,
                Tagger(self.repository['content'])))

    def test_tagger_should_be_empty_if_not_tagged(self):
        tagger = Tagger(ExampleContentType())
        self.assertEqual([], list(tagger))

    def test_tagger_should_get_tags_from_content(self):
        content = create_testcontent()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-berlin">Berlin</tag>
""")
        tagger = Tagger(content)
        self.assertEqual(set([u'☃Berlin', u'☃Karen Duve']), set(tagger))

    def test_len_should_return_amount_of_tags(self):
        content = create_testcontent()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-berlin">Berlin</tag>
""")
        tagger = Tagger(content)
        self.assertEqual(2, len(tagger))
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-berlin">Berlin</tag>
<tag uuid="uid-fleisch">Fleisch</tag>
""")
        self.assertEqual(3, len(tagger))

    def test_tags_should_be_accessible_by_id(self):
        content = create_testcontent()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-berlin">Berlin</tag>
""")
        tagger = Tagger(content)
        tag = tagger[u'☃Karen Duve']
        self.assertEqual(tagger, tag.__parent__)
        self.assertEqual(u'☃Karen Duve', tag.__name__)
        self.assertEqual('Karen Duve', tag.label)

    def test_tag_should_have_entity_type(self):
        content = create_testcontent()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-berlin" type="Location">Berlin</tag>
""")
        tagger = Tagger(content)
        self.assertEqual('Location', tagger[u'Location☃Berlin'].entity_type)

    def test_tag_should_convert_unicode_symbols_to_nice_ascii_urls(self):
        content = create_testcontent()
        self.set_tags(content, """<tag>Bärlön</tag>""")
        tagger = Tagger(content)
        self.assertEqual(
            'tag://\\u2603B\\xe4rl\\xf6n', tagger[u'☃Bärlön'].uniqueId)

    def test_getitem_should_raise_keyerror_if_tag_does_not_exist(self):
        tagger = Tagger(ExampleContentType())
        self.assertRaises(KeyError, lambda: tagger['foo'])

    def test_iter_includes_tags_with_and_without_uuids(self):
        content = create_testcontent()
        self.set_tags(content, """
<tag>Karen Duve</tag>
<tag uuid="uid-berlin">Berlin</tag>
""")
        tagger = Tagger(content)
        self.assertEqual([u'☃Karen Duve', u'☃Berlin'], list(tagger))

    def test_setitem_should_add_tag(self):
        tagger = Tagger(ExampleContentType())
        tagger[u'☃Berlin'] = Tag('Berlin', '')
        self.assertEqual([u'☃Berlin'], list(tagger))
        self.assertEqual('Berlin', tagger[u'☃Berlin'].label)

    def test_setitem_should_set_entity_type(self):
        tagger = Tagger(ExampleContentType())
        tagger[u'☃Berlin'] = Tag(
            'Berlin', entity_type='Location')
        self.assertEqual('Location', tagger[u'Location☃Berlin'].entity_type)

    def test_iter_should_be_sorted_by_document_order(self):
        content = create_testcontent()
        self.set_tags(content, """
<tag uuid="uid-berlin">Berlin</tag>
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-fleisch">Fleisch</tag>
""")
        tagger = Tagger(content)
        self.assertEqual(
            [u'☃Berlin', u'☃Karen Duve', u'☃Fleisch'], list(tagger))

    def test_updateOrder_should_sort_tags(self):
        content = create_testcontent()
        self.set_tags(content, """
<tag uuid="uid-berlin">Berlin</tag>
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-fleisch">Fleisch</tag>
""")
        tagger = Tagger(content)
        tagger.updateOrder([u'☃Fleisch', u'☃Berlin', u'☃Karen Duve'])
        self.assertEqual(
            [u'☃Fleisch', u'☃Berlin', u'☃Karen Duve'], list(tagger))

    def test_updateOrder_should_sort_tags_even_when_keys_are_generator(self):
        content = create_testcontent()
        self.set_tags(content, """
<tag uuid="uid-berlin">Berlin</tag>
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-fleisch">Fleisch</tag>
""")
        tagger = Tagger(content)
        tagger.updateOrder(
            iter([u'☃Fleisch', u'☃Berlin', u'☃Karen Duve']))
        self.assertEqual(
            [u'☃Fleisch', u'☃Berlin', u'☃Karen Duve'], list(tagger))

    def test_given_keys_differ_from_existing_keys_should_raise(self):
        content = create_testcontent()
        self.set_tags(content, """
<tag uuid="uid-berlin">Berlin</tag>
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-fleisch">Fleisch</tag>
""")
        tagger = Tagger(content)
        self.assertRaises(
            ValueError,
            lambda: tagger.updateOrder(['uid-berlin', 'uid-karenduve']))

    def test_contains_should_return_true_for_existing_tag(self):
        content = create_testcontent()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
""")
        tagger = Tagger(content)
        self.assertIn(u'☃Karen Duve', tagger)

    def test_contains_should_return_false_for_noneexisting_tag(self):
        content = create_testcontent()
        tagger = Tagger(content)
        self.assertNotIn(u'☃Karen Duve', tagger)

    def test_get_should_return_existing_tag(self):
        content = create_testcontent()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
""")
        tagger = Tagger(content)
        self.assertEqual('Karen Duve', tagger.get(u'☃Karen Duve').label)

    def test_get_should_return_default_if_tag_does_not_exist(self):
        content = create_testcontent()
        tagger = Tagger(content)
        self.assertEqual(mock.sentinel.default,
                         tagger.get('uid-karenduve', mock.sentinel.default))

    def test_delitem_should_remove_tag(self):
        content = create_testcontent()
        # use an umlaut to exercise serialization
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Düve</tag>
""")
        tagger = Tagger(content)
        del tagger[u'☃Karen Düve']
        self.assertNotIn(u'☃Karen Düve', tagger)

    def test_delitem_should_add_tag_to_disabled_list_in_dav(self):
        content = create_testcontent()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
""")
        tagger = Tagger(content)
        del tagger[u'☃Karen Duve']

        dav = zeit.connector.interfaces.IWebDAVProperties(content)
        dav_key = ('disabled', 'http://namespaces.zeit.de/CMS/tagging')
        self.assertEqual(u'☃Karen Duve', dav[dav_key])

    def test_disabled_tags_should_be_separated_by_tab(self):
        content = create_testcontent()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-berlin">Berlin</tag>
""")
        tagger = Tagger(content)
        del tagger[u'☃Karen Duve']
        del tagger[u'☃Berlin']

        dav = zeit.connector.interfaces.IWebDAVProperties(content)
        dav_key = ('disabled', 'http://namespaces.zeit.de/CMS/tagging')
        self.assertEqual(u'☃Karen Duve\t☃Berlin', dav[dav_key])

    def test_no_disabled_tags_should_return_empty_tuple(self):
        content = create_testcontent()
        tagger = Tagger(content)
        self.assertEqual((), tagger.disabled)
        dav = zeit.connector.interfaces.IWebDAVProperties(content)
        dav_key = ('disabled', 'http://namespaces.zeit.de/CMS/tagging')
        dav[dav_key] = u''
        self.assertEqual((), tagger.disabled)

    def test_to_xml_should_return_inner_rankedTags(self):
        content = create_testcontent()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-berlin">Berlin</tag>
""")
        tagger = Tagger(content)
        node = tagger.to_xml()
        self.assertEqual('rankedTags', node.tag)

    def test_rankedTags_dav_property_should_not_be_added_to_xml_directly(self):
        content = create_testcontent()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-berlin">Berlin</tag>
""")
        zope.interface.alsoProvides(
            content, zeit.cms.content.interfaces.IDAVPropertiesInXML)
        sync = zeit.cms.content.interfaces.IDAVPropertyXMLSynchroniser(content)
        sync.sync()
        dav_attribs = u'\n'.join(
            six.text_type(a) for a in content.xml.head.attribute[:])
        self.assertNotIn('rankedTags', dav_attribs)

    def test_existing_tags_should_cause_rankedTags_to_be_added_to_xml(self):
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        repository['content'] = create_testcontent()
        with checked_out(repository['content']) as content:
            self.set_tags(content, """
    <tag uuid="uid-karenduve">Karen Duve</tag>
    <tag uuid="uid-berlin">Berlin</tag>
    """)
        self.assertEqual(
            ['Karen Duve', 'Berlin'],
            repository['content'].xml.head.rankedTags.getchildren())

    def test_no_tags_cause_rankedTags_element_to_be_removed_from_xml(self):
        content = create_testcontent()
        content.xml.head.rankedTags = 'bla bla bla'
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        repository['content'] = content
        with checked_out(repository['content']):
            # cycle
            pass
        self.assertNotIn('rankedTags', repository['content'].xml.head.keys())

    def test_checkin_should_not_fail_with_no_tags_and_no_rankedTags_element(
            self):
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        repository['content'] = create_testcontent()
        with checked_out(repository['content']):
            # cycle
            pass

    def test_disabled_tags_should_be_removed_from_xml(self):
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        repository['content'] = create_testcontent()
        with checked_out(repository['content']) as \
                content:
            self.set_tags(content, """
    <tag uuid="uid-karenduve">Karen Duve</tag>
    <tag uuid="uid-berlin">Berlin</tag>
    """)
            tagger = Tagger(content)
            del tagger[u'☃Berlin']
        self.assertEqual(
            ['Karen Duve'],
            repository['content'].xml.head.rankedTags.getchildren())

    def test_rankedTags_in_xml_should_be_updated_on_modified_event(self):
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        repository['content'] = create_testcontent()
        with checked_out(repository['content']) as content:
            self.set_tags(content, """
    <tag uuid="uid-karenduve">Karen Duve</tag>
    <tag uuid="uid-berlin">Berlin</tag>
    """)
            zope.lifecycleevent.modified(content)
            self.assertEqual(
                ['Karen Duve', 'Berlin'],
                content.xml.head.rankedTags.getchildren())

    def test_modified_event_should_leave_non_content_alone(self):
        # regression #12394
        dummy = type('Dummy', (object,), {})
        zope.interface.alsoProvides(
            dummy, zeit.cms.content.interfaces.IXMLRepresentation)
        with mock.patch(
                'zeit.cms.tagging.tag.add_ranked_tags_to_head') as handler:
            zope.lifecycleevent.modified(dummy)
            self.assertFalse(handler.called)

    def test_set_pinned_should_update_tab_separated_property(self):
        content = create_testcontent()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-berlin">Berlin</tag>
""")
        tagger = Tagger(content)
        tagger.set_pinned([u'☃Berlin', u'☃Karen Duve'])
        self.assertEqual((u'☃Berlin', u'☃Karen Duve'), tagger.pinned)

        dav = zeit.connector.interfaces.IWebDAVProperties(content)
        dav_key = ('pinned', 'http://namespaces.zeit.de/CMS/tagging')
        self.assertEqual(u'☃Berlin\t☃Karen Duve', dav[dav_key])

        self.assertTrue(tagger[u'☃Berlin'].pinned)

    def test_iterating_values_calls_to_xml_only_once(self):
        # We do not want to reuse `__iter__` and `__getitem__` in values, since
        # that would call `_find_tag_node` & `to_xml` for *each* keyword.
        content = create_testcontent()
        tagger = Tagger(content)
        with mock.patch('zeit.retresco.tagger.Tagger.to_xml') as to_xml:
            to_xml.return_value = lxml.objectify.fromstring("""
<rankedTags>
    <tag uuid="uid-karenduve">Karen Duve</tag>
    <tag uuid="uid-berlin">Berlin</tag>
</rankedTags>""")
            self.assertEqual(2, len(list(tagger.values())))
            self.assertEqual(1, to_xml.call_count)

    def test_values_returns_empty_iterator_if_no_values(self):
        content = create_testcontent()
        tagger = Tagger(content)
        self.assertEqual([], list(tagger.values()))

    def test_tags_retrieved_via_values_remain_pinned(self):
        content = create_testcontent()
        self.set_tags(content, """<tag uuid="uid-berlin">Berlin</tag>""")
        tagger = Tagger(content)
        tagger.set_pinned([u'☃Berlin'])
        self.assertEqual(True, next(tagger.values()).pinned)

    def test_to_xml_returns_empty_when_no_rankedTags_tag_was_found(self):
        content = create_testcontent()
        tagger = Tagger(content)
        self.assertEqual(Tagger.EMPTY_NODE, tagger.to_xml())

    def test_to_xml_returns_empty_when_keyword_DAV_property_is_malformed(self):
        content = create_testcontent()
        dav = zeit.connector.interfaces.IWebDAVProperties(content)
        dav[('rankedTags',
             'http://namespaces.zeit.de/CMS/tagging')] = "<foobar/>"
        tagger = Tagger(content)
        self.assertEqual(Tagger.EMPTY_NODE, tagger.to_xml())

    def test_getitem_raises_key_error_when_no_keywords_are_present(self):
        content = create_testcontent()
        tagger = Tagger(content)
        with self.assertRaises(KeyError):
            tagger['i-do-not-exist']

    def test_getitem_raises_key_error_if_no_tag_matches(self):
        content = create_testcontent()
        self.set_tags(content, """<tag uuid="uid-berlin">Berlin</tag>""")
        tagger = Tagger(content)
        with self.assertRaises(KeyError):
            tagger['i-do-not-exist']

    def test_tagger_raises_error_on_keys_and_items(self):
        # We do not use keys and items yet but the interface requires them.
        content = create_testcontent()
        tagger = Tagger(content)
        with self.assertRaises(NotImplementedError):
            tagger.keys()
        with self.assertRaises(NotImplementedError):
            tagger.items()

    def test_ignores_xml_attributes_besides_entity_type(self):
        content = create_testcontent()
        self.set_tags(content, """
<tag type="Snowpeople" url_value="url" uuid="uuid-tag">Snowman Tag</tag>
""")
        tagger = Tagger(content)
        snowman = tagger[u'Snowpeople☃Snowman Tag']
        self.assertEqual(
            [u'Snowman Tag', u'Snowpeople'],
            [snowman.label, snowman.entity_type])


class TaggerUpdateTest(
        zeit.retresco.testing.FunctionalTestCase,
        zeit.retresco.testing.TagTestHelpers):

    def test_update_should_keep_pinned_tags(self):
        content = create_testcontent()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>""")
        tagger = Tagger(content)
        tagger.set_pinned([u'☃Karen Duve'])
        tagger.update()
        self.assertEqual([u'☃Karen Duve'], list(tagger))

    def test_update_should_not_duplicate_pinned_tags(self):
        # this is a rather tricky edge case:
        # when we pin a manual tag first, and then also pin a tag that
        # comes in via update() again, we used to screw it up,
        # since we compared against a generator multiple times
        extract_keywords = 'zeit.retresco.connection.TMS.extract_keywords'
        with mock.patch(extract_keywords) as extract_keywords:
            extract_keywords.return_value = [
                Tag('Foo', ''), Tag('Bar', '')]
            content = create_testcontent()
            tagger = Tagger(content)
            tagger.update()
            self.assertEqual(2, len(tagger))
            tagger[u'☃Qux'] = Tag('Qux', '')
            tagger.set_pinned([u'☃Qux', u'☃Foo'])
            tagger.update()
            self.assertEqual(
                [u'Foo', u'Bar', u'Qux'],
                [tagger[x].label.strip() for x in tagger])

    def test_update_should_discard_disabled_tags(self):
        extract_keywords = 'zeit.retresco.connection.TMS.extract_keywords'
        with mock.patch(extract_keywords) as extract_keywords:
            extract_keywords.return_value = [
                Tag('Foo', ''), Tag('Bar', '')]
            content = create_testcontent()
            tagger = Tagger(content)
            tagger.update()
            self.assertEqual(2, len(tagger))
            del tagger[u'☃Foo']
            tagger.update()
            self.assertEqual([u'☃Bar'], list(tagger))

    def test_update_should_clear_disabled_tags(self):
        content = create_testcontent()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>""")
        tagger = Tagger(content)
        del tagger[u'☃Karen Duve']
        tagger.update()
        dav = zeit.connector.interfaces.IWebDAVProperties(content)
        dav_key = ('disabled', 'http://namespaces.zeit.de/CMS/tagging')
        self.assertEqual('', dav[dav_key])

    def test_update_with_option_should_not_clear_disabled_tags(self):
        content = create_testcontent()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>""")
        tagger = Tagger(content)
        del tagger[u'☃Karen Duve']
        tagger.update(clear_disabled=False)
        dav = zeit.connector.interfaces.IWebDAVProperties(content)
        dav_key = ('disabled', 'http://namespaces.zeit.de/CMS/tagging')
        self.assertEqual(u'☃Karen Duve', dav[dav_key])

    def test_update_should_pass_existing_tags_to_tms(self):
        content = create_testcontent()
        self.set_tags(content, """
<tag uuid="uid-karenduve" type="keyword">Karen Duve</tag>
<tag uuid="uid-berlin" type="location">Berlin</tag>""")
        tagger = Tagger(content)
        with mock.patch('zeit.retresco.connection.TMS._request') as request:
            tagger.update()
            data = request.call_args[1]['json']
            self.assertEqual(['Karen Duve'], data['rtr_keywords'])
            self.assertEqual(['Berlin'], data['rtr_locations'])

    def test_links_to_topicpages_are_retrieved_from_tms(self):
        content = create_testcontent()
        tagger = Tagger(content)
        article_keywords = 'zeit.retresco.connection.TMS.get_article_keywords'
        with mock.patch(article_keywords) as article_keywords:
            tag1 = Tag('Foo', '')
            tag1.link = 'thema/foo'
            tag2 = Tag('Bar', '')
            article_keywords.return_value = [tag1, tag2]
            self.assertEqual({
                tag1.uniqueId: 'http://localhost/live-prefix/thema/foo',
                tag2.uniqueId: None,
            }, tagger.links)

    @unittest.skipUnless(HAVE_INTRAFIND, 'zeit.intrafind not available')
    def test_update_should_keep_intrafind_pinned_tags(self):
        content = create_testcontent()
        intra = zeit.intrafind.tagger.Tagger(content)
        intra['uid-intra'] = zeit.intrafind.tag.Tag(
            'uid-intra', 'Berlin', entity_type='free')
        intra.set_pinned(['uid-intra'])
        tagger = Tagger(content)
        tagger.update()
        self.assertEqual([u'keyword☃Berlin'], list(tagger))
        self.assertEqual((u'keyword☃Berlin',), tagger.pinned)

        # Pinned are converted to TMS ids, so intrafind is no longer relevant.
        del intra['uid-intra']
        tagger.update()
        self.assertEqual([u'keyword☃Berlin'], list(tagger))
        self.assertEqual((u'keyword☃Berlin',), tagger.pinned)
