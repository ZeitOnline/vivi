# coding: utf8
from zeit.cms.checkout.helper import checked_out
from zeit.cms.tagging.tag import Tag
from zeit.cms.testcontenttype.testcontenttype import TestContentType
from zeit.retresco.keywords import Tagger
import mock
import zeit.cms.content.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.tagging.interfaces
import zeit.cms.testcontenttype.testcontenttype
import zeit.cms.testing
import zeit.connector.interfaces
import zeit.retresco.keywords
import zeit.retresco.testing
import zope.component
import zope.interface
import zope.interface.verify
import zope.lifecycleevent


class TagTestHelpers(object):

    def set_tags(self, content, xml):
        dav = zeit.connector.interfaces.IWebDAVProperties(content)
        name, ns = dav_key = (
            'rankedTags', 'http://namespaces.zeit.de/CMS/tagging')
        dav[dav_key] = """<ns:{tag} xmlns:ns="{ns}">
        <rankedTags>{0}</rankedTags></ns:{tag}>""".format(
            xml, ns=ns, tag=name)


class TestTagger(zeit.cms.testing.FunctionalTestCase, TagTestHelpers):

    layer = zeit.retresco.testing.ZCML_LAYER

    def test_tagger_should_provide_interface(self):
        self.assertTrue(
            zope.interface.verify.verifyObject(
                zeit.cms.tagging.interfaces.ITagger,
                Tagger(TestContentType())))

    def test_tagger_should_be_empty_if_not_tagged(self):
        tagger = Tagger(TestContentType())
        self.assertEqual([], list(tagger))

    def test_tagger_should_get_tags_from_content(self):
        content = TestContentType()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-berlin">Berlin</tag>
""")
        tagger = Tagger(content)
        self.assertEqual(set(['uid-berlin', 'uid-karenduve']), set(tagger))

    def test_len_should_return_amount_of_tags(self):
        content = TestContentType()
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
        content = TestContentType()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-berlin">Berlin</tag>
""")
        tagger = Tagger(content)
        tag = tagger['uid-karenduve']
        self.assertEqual(tagger, tag.__parent__)
        self.assertEqual('uid-karenduve', tag.__name__)
        self.assertEqual('Karen Duve', tag.label)

    def test_tag_should_have_entity_type(self):
        content = TestContentType()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-berlin" type="Location">Berlin</tag>
""")
        tagger = Tagger(content)
        self.assertEqual('Location', tagger['uid-berlin'].entity_type)

    def test_tag_should_have_url_value(self):
        content = TestContentType()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-berlin" url_value="dickesb">Berlin</tag>
""")
        tagger = Tagger(content)
        self.assertEqual('dickesb', tagger['uid-berlin'].url_value)

    def test_getitem_should_raise_keyerror_if_tag_does_not_exist(self):
        tagger = Tagger(TestContentType())
        self.assertRaises(KeyError, lambda: tagger['foo'])

    def test_iter_ignores_tags_without_uuids(self):
        content = TestContentType()
        self.set_tags(content, """
<tag>Karen Duve</tag>
<tag uuid="uid-berlin">Berlin</tag>
""")
        tagger = Tagger(content)
        self.assertEqual(['uid-berlin'], list(tagger))

    def test_setitem_should_add_tag(self):
        tagger = Tagger(TestContentType())
        tagger['uid-berlin'] = Tag('uid-berlin', 'Berlin')
        self.assertEqual(['uid-berlin'], list(tagger))
        self.assertEqual('Berlin', tagger['uid-berlin'].label)

    def test_setitem_should_set_entity_type(self):
        tagger = Tagger(TestContentType())
        tagger['uid-berlin'] = Tag(
            'uid-berlin', 'Berlin', entity_type='Location')
        self.assertEqual('Location', tagger['uid-berlin'].entity_type)

    def test_iter_should_be_sorted_by_document_order(self):
        content = TestContentType()
        self.set_tags(content, """
<tag uuid="uid-berlin">Berlin</tag>
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-fleisch">Fleisch</tag>
""")
        tagger = Tagger(content)
        self.assertEqual(
            ['uid-berlin', 'uid-karenduve', 'uid-fleisch'], list(tagger))

    def test_updateOrder_should_sort_tags(self):
        content = TestContentType()
        self.set_tags(content, """
<tag uuid="uid-berlin">Berlin</tag>
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-fleisch">Fleisch</tag>
""")
        tagger = Tagger(content)
        tagger.updateOrder(['uid-fleisch', 'uid-berlin', 'uid-karenduve'])
        self.assertEqual(
            ['uid-fleisch', 'uid-berlin', 'uid-karenduve'], list(tagger))

    def test_updateOrder_should_sort_tags_even_when_keys_are_generator(self):
        content = TestContentType()
        self.set_tags(content, """
<tag uuid="uid-berlin">Berlin</tag>
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-fleisch">Fleisch</tag>
""")
        tagger = Tagger(content)
        tagger.updateOrder(
            iter(['uid-fleisch', 'uid-berlin', 'uid-karenduve']))
        self.assertEqual(
            ['uid-fleisch', 'uid-berlin', 'uid-karenduve'], list(tagger))

    def test_given_keys_differ_from_existing_keys_should_raise(self):
        content = TestContentType()
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
        content = TestContentType()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
""")
        tagger = Tagger(content)
        self.assertIn('uid-karenduve', tagger)

    def test_contains_should_return_false_for_noneexisting_tag(self):
        content = TestContentType()
        tagger = Tagger(content)
        self.assertNotIn('uid-karenduve', tagger)

    def test_get_should_return_existing_tag(self):
        content = TestContentType()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
""")
        tagger = Tagger(content)
        self.assertEqual('Karen Duve', tagger.get('uid-karenduve').label)

    def test_get_should_return_default_if_tag_does_not_exist(self):
        content = TestContentType()
        tagger = Tagger(content)
        self.assertEqual(mock.sentinel.default,
                         tagger.get('uid-karenduve', mock.sentinel.default))

    def test_delitem_should_remove_tag(self):
        content = TestContentType()
        # use an umlaut to exercise serialization
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Düve</tag>
""")
        tagger = Tagger(content)
        del tagger['uid-karenduve']
        self.assertNotIn('uid-karenduve', tagger)

    def test_delitem_should_add_tag_to_disabled_list_in_dav(self):
        content = TestContentType()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
""")
        tagger = Tagger(content)
        del tagger['uid-karenduve']

        dav = zeit.connector.interfaces.IWebDAVProperties(content)
        dav_key = ('disabled', 'http://namespaces.zeit.de/CMS/tagging')
        self.assertEqual('uid-karenduve', dav[dav_key])

    def test_disabled_tags_should_be_separated_by_tab(self):
        content = TestContentType()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-berlin">Berlin</tag>
""")
        tagger = Tagger(content)
        del tagger['uid-karenduve']

        dav = zeit.connector.interfaces.IWebDAVProperties(content)
        dav_key = ('disabled', 'http://namespaces.zeit.de/CMS/tagging')
        self.assertEqual('uid-karenduve', dav[dav_key])

    def test_to_xml_should_return_inner_rankedTags(self):
        content = TestContentType()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-berlin">Berlin</tag>
""")
        tagger = Tagger(content)
        node = tagger.to_xml()
        self.assertEqual('rankedTags', node.tag)

    def test_rankedTags_dav_property_should_not_be_added_to_xml_directly(self):
        content = TestContentType()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-berlin">Berlin</tag>
""")
        zope.interface.alsoProvides(
            content, zeit.cms.content.interfaces.IDAVPropertiesInXML)
        sync = zeit.cms.content.interfaces.IDAVPropertyXMLSynchroniser(content)
        sync.sync()
        dav_attribs = u'\n'.join(
            unicode(a) for a in content.xml.head.attribute[:])
        self.assertNotIn('rankedTags', dav_attribs)

    def test_existing_tags_should_cause_rankedTags_to_be_added_to_xml(self):
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        repository['content'] = TestContentType()
        with checked_out(repository['content']) as content:
            self.set_tags(content, """
    <tag uuid="uid-karenduve">Karen Duve</tag>
    <tag uuid="uid-berlin">Berlin</tag>
    """)
        self.assertEqual(
            ['Karen Duve', 'Berlin'],
            repository['content'].xml.head.rankedTags.getchildren())

    def test_no_tags_cause_rankedTags_element_to_be_removed_from_xml(self):
        content = TestContentType()
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
        repository['content'] = TestContentType()
        with checked_out(repository['content']):
            # cycle
            pass

    def test_disabled_tags_should_be_removed_from_xml(self):
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        repository['content'] = TestContentType()
        with zeit.cms.checkout.helper.checked_out(repository['content']) as \
                content:
            self.set_tags(content, """
    <tag uuid="uid-karenduve">Karen Duve</tag>
    <tag uuid="uid-berlin">Berlin</tag>
    """)
            tagger = Tagger(content)
            del tagger['uid-berlin']
        self.assertEqual(
            ['Karen Duve'],
            repository['content'].xml.head.rankedTags.getchildren())

    def test_rankedTags_in_xml_should_be_updated_on_modified_event(self):
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        repository['content'] = TestContentType()
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
        content = TestContentType()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>
<tag uuid="uid-berlin">Berlin</tag>
""")
        tagger = Tagger(content)
        tagger.set_pinned(['uid-berlin', 'uid-karenduve'])
        self.assertEqual(('uid-berlin', 'uid-karenduve'), tagger.pinned)

        dav = zeit.connector.interfaces.IWebDAVProperties(content)
        dav_key = ('pinned', 'http://namespaces.zeit.de/CMS/tagging')
        self.assertEqual('uid-berlin\tuid-karenduve', dav[dav_key])

        self.assertTrue(tagger['uid-berlin'].pinned)


class TaggerUpdateTest(zeit.cms.testing.FunctionalTestCase, TagTestHelpers):

    layer = zeit.retresco.testing.ZCML_LAYER

    def test_update_should_keep_pinned_tags(self):
        content = TestContentType()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>""")
        tagger = Tagger(content)
        tagger.set_pinned(['uid-karenduve'])
        tagger.update()
        self.assertEqual(['uid-karenduve'], list(tagger))

    def test_update_should_not_duplicate_pinned_tags(self):
        # this is a rather tricky edge case:
        # when we pin a manual tag first, and then also pin a tag that
        # comes in via update() again, we used to screw it up,
        # since we compared against a generator multiple times
        with mock.patch(
                'zeit.retresco.connection.TMS.get_keywords') as get_keywords:
            get_keywords.return_value = [
                Tag('uid-foo', 'Foo'), Tag('uid-bar', 'Bar')]
            content = TestContentType()
            tagger = Tagger(content)
            tagger.update()
            self.assertEqual(2, len(tagger))
            tagger['uid-qux'] = Tag('uid-qux', 'Qux')
            tagger.set_pinned(['uid-qux', 'uid-foo'])
            tagger.update()
            self.assertEqual(
                [u'Foo', u'Bar', u'Qux'],
                [tagger[x].label.strip() for x in tagger])

    def test_update_should_discard_disabled_tags(self):
        with mock.patch(
                'zeit.retresco.connection.TMS.get_keywords') as get_keywords:
            get_keywords.return_value = [
                Tag('uid-foo', 'Foo'), Tag('uid-bar', 'Bar')]
            content = TestContentType()
            tagger = Tagger(content)
            tagger.update()
            self.assertEqual(2, len(tagger))
            del tagger['uid-foo']
            tagger.update()
            self.assertEqual(['uid-bar'], list(tagger))

    def test_update_should_clear_disabled_tags(self):
        content = TestContentType()
        self.set_tags(content, """
<tag uuid="uid-karenduve">Karen Duve</tag>""")
        tagger = Tagger(content)
        del tagger['uid-karenduve']
        tagger.update()
        dav = zeit.connector.interfaces.IWebDAVProperties(content)
        dav_key = ('disabled', 'http://namespaces.zeit.de/CMS/tagging')
        self.assertEqual('', dav[dav_key])
