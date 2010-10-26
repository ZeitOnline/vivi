# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest
import zeit.content.article.testing


class ReferenceTest(unittest.TestCase):

    @property
    def test_class(self):
        from zeit.content.article.edit.reference import Reference
        return Reference

    def get_ref(self):
        import lxml.objectify
        tree = lxml.objectify.E.tree(
            lxml.objectify.E.ref())
        ref = self.test_class(None, tree.ref)
        ref._validate = mock.Mock()
        return ref

    def test_reference_gets_object_from_href(self):
        ref = self.get_ref()
        ref.xml.set('href', 'auniqueid')
        with mock.patch('zeit.cms.interfaces.ICMSContent') as icc:
            result = ref.references
            self.assertEqual(icc.return_value, result)
            icc.assert_called_with('auniqueid', None)

    def test_empty_href_returns_none(self):
        ref = self.get_ref()
        self.assertEqual(None, ref.references)

    def test_wrong_href_returns_none(self):
        ref = self.get_ref()
        ref.xml.set('href', 'foo')
        self.assertEqual(None, ref.references)

    def test_setting_object_should_set_href(self):
        ref = self.get_ref()
        obj = mock.Mock()
        obj.uniqueId = 'my-id'
        ref.references = obj
        self.assertEqual('my-id', ref.xml.get('href'))

    def test_setting_none_removes_href(self):
        ref = self.get_ref()
        ref.xml.set('href', 'auniqueid')
        ref.references = None
        self.assertFalse('href' in ref.xml.attrib)
        # second assignment doesn't fail
        ref.references = None

    def test_setting_object_should_update_node_with_xmlreferenceupdater(self):
        ref = self.get_ref()
        obj = mock.Mock()
        obj.uniqueId = 'my-id'
        with mock.patch('zeit.cms.content.interfaces.IXMLReferenceUpdater') as\
            xru:
            ref.references = obj
            xru.assert_called_with(obj, None)
            xru.return_value.update.assert_called_with(ref.xml)

    def test_setting_none_removes_other_attributes_and_child_nodes(self):
        ref = self.get_ref()
        ref.xml.set('href', 'auniqueid')
        ref.xml.set('honk', 'hubbel')
        ref.__name__ = 'myname'  # name is kept!
        ref.xml.achild = 'mary had a little lamb'
        ref.references = None
        self.assertFalse('honk' in ref.xml.attrib)
        self.assertEqual('myname', ref.__name__)
        self.assertEqual([], ref.xml.getchildren())
        # second assignment doesn't fail
        ref.references = None


class TestGallery(ReferenceTest):

    @property
    def test_class(self):
        from zeit.content.article.edit.reference import Gallery
        return Gallery


class TestFactories(zeit.content.article.testing.FunctionalTestCase):

    def assert_factory(self, name, title, interface):
        import zeit.content.article.article
        import zeit.content.article.edit.body
        import zeit.edit.interfaces
        import zope.component
        article = zeit.content.article.article.Article()
        body = zeit.content.article.edit.body.EditableBody(
            article, article.xml.body)
        factory = zope.component.getAdapter(
            body, zeit.edit.interfaces.IElementFactory, name)
        self.assertEqual(title, factory.title)
        div = factory()
        self.assertTrue(interface.providedBy(div))
        self.assertEqual(name, div.xml.tag)

    def test_gallery_factory(self):
        from zeit.content.article.edit.interfaces import IGallery
        self.assert_factory('gallery', 'Gallery', IGallery)
