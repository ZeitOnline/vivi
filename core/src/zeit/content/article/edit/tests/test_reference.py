from unittest import mock
import unittest

import lxml.builder
import zope.lifecycleevent

from zeit.cms.checkout.helper import checked_out
import zeit.content.article.testing


class ReferenceTest(unittest.TestCase):
    @property
    def test_class(self):
        from zeit.content.article.edit.reference import Reference

        return Reference

    def get_ref(self):
        ref = lxml.builder.E.ref()
        lxml.builder.E.tree(ref)
        ref = self.test_class(None, ref)
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

    def test_setting_none_removes_other_attributes_and_child_nodes(self):
        ref = self.get_ref()
        ref.xml.set('href', 'auniqueid')
        ref.xml.set('honk', 'hubbel')
        ref.__name__ = 'myname'  # name is kept!
        ref.xml.append(lxml.builder.E.achild('mary had a little lamb'))
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


class TestInfobox(ReferenceTest):
    @property
    def test_class(self):
        from zeit.content.article.edit.reference import Infobox

        return Infobox

    def test_no_layout_set_should_return_default(self):
        ref = self.get_ref()
        self.assertEqual('default', ref.layout)

    def test_layout_should_set_attribute(self):
        ref = self.get_ref()
        ref.layout = 'debatte'
        self.assertEqual('debatte', ref.xml.get('layout'))


class TestPortraitbox(ReferenceTest):
    @property
    def test_class(self):
        from zeit.content.article.edit.reference import Portraitbox

        return Portraitbox

    def test_default_layout_should_be_set(self):
        ref = self.get_ref()
        self.assertEqual('short', ref.xml.get('layout'))

    def test_stored_layout_should_be_returned(self):
        ref = self.get_ref()
        ref.layout = 'wide'
        ref = self.test_class(None, ref.xml)
        self.assertEqual('wide', ref.xml.get('layout'))

    def test_layout_should_set_attribute(self):
        ref = self.get_ref()
        ref.layout = 'wide'
        self.assertEqual('wide', ref.xml.get('layout'))

    def test_default_name_should_be_read_from_referenced_box(self):
        ref = self.get_ref()
        with mock.patch('zeit.content.article.edit.reference.Portraitbox.references') as pbox:
            pbox.name = 'ref-name'
            self.assertEqual(ref.name, 'ref-name')

    def test_local_name_should_override_value_from_referenced_box(self):
        ref = self.get_ref()
        with mock.patch('zeit.content.article.edit.reference.Portraitbox.references') as pbox:
            pbox.name = 'ref-name'
            ref.name = 'local-name'
            self.assertEqual(ref.name, 'local-name')

    def test_default_text_should_be_read_from_referenced_box(self):
        ref = self.get_ref()
        with mock.patch('zeit.content.article.edit.reference.Portraitbox.references') as pbox:
            pbox.text = 'ref-text'
            self.assertEqual(ref.text, 'ref-text')

    def test_local_text_should_override_value_from_referenced_box(self):
        ref = self.get_ref()
        with mock.patch('zeit.content.article.edit.reference.Portraitbox.references') as pbox:
            pbox.text = 'ref-text'
            ref.text = 'local-text'
            self.assertEqual(ref.text, 'local-text')


class TestFactories(zeit.content.article.testing.FunctionalTestCase):
    def assert_factory(self, name, title, interface):
        import zope.component

        import zeit.content.article.article
        import zeit.content.article.edit.body
        import zeit.edit.interfaces

        article = zeit.content.article.article.Article()
        body = zeit.content.article.edit.body.EditableBody(article, article.xml.find('body'))
        factory = zope.component.getAdapter(body, zeit.edit.interfaces.IElementFactory, name)
        self.assertEqual(title, factory.title)
        div = factory()
        self.assertTrue(interface.providedBy(div))
        self.assertEqual(name, div.xml.tag)

    def test_gallery_factory(self):
        from zeit.content.article.edit.interfaces import IGallery

        self.assert_factory('gallery', 'Gallery', IGallery)

    def test_infobox_factory(self):
        from zeit.content.article.edit.interfaces import IInfobox

        self.assert_factory('infobox', 'Infobox', IInfobox)

    def test_portraitbox_factory(self):
        from zeit.content.article.edit.interfaces import IPortraitbox

        self.assert_factory('portraitbox', 'Portraitbox', IPortraitbox)


class TestMetadataUpdate(zeit.content.article.testing.FunctionalTestCase):
    def setUp(self):
        # We do not want a fake tagger as Portraitbox and Infobox do not
        # support tagging in the real world, so skip the setup of the parent
        # class and doe the one of the grandparent.
        super(zeit.content.article.testing.FunctionalTestCase, self).setUp()

    def test_empty_reference_should_not_break_metadata_update(self):
        for typ in ['gallery', 'portraitbox', 'infobox', 'image', 'author', 'volume']:
            article = self.get_article()
            self.get_factory(article, typ)()
            self.repository['article'] = article
            with self.assertNothingRaised():
                with checked_out(self.repository['article']):
                    pass


class EmptyMarkerTest:
    block_type = NotImplemented

    def create_block(self):
        return self.get_factory(self.get_article(), self.block_type)()

    def create_target(self):
        raise NotImplementedError()

    def set_reference(self, block, target):
        block.references = target

    def test_block_is_empty_after_creation(self):
        block = self.create_block()
        self.assertTrue(block.is_empty)
        body = block.__parent__
        self.assertTrue(body.values()[0].is_empty)

    def test_setting_nonempty_is_persisted(self):
        block = self.create_block()
        block.is_empty = False
        body = block.__parent__
        self.assertFalse(body.values()[0].is_empty)

    def test_block_is_not_empty_after_setting_reference(self):
        block = self.create_block()
        self.set_reference(block, self.create_target())
        zope.lifecycleevent.modified(block)
        self.assertFalse(block.is_empty)

    def test_block_is_empty_after_removing_reference(self):
        block = self.create_block()
        self.set_reference(block, self.create_target())
        zope.lifecycleevent.modified(block)
        self.set_reference(block, None)
        zope.lifecycleevent.modified(block)
        self.assertTrue(block.is_empty)

    def test_block_is_not_empty_when_created_from_reference(self):
        article = self.get_article()
        body = zeit.content.article.edit.body.EditableBody(article, article.xml.find('body'))
        block = zope.component.getMultiAdapter(
            (body, self.create_target(), 0), zeit.edit.interfaces.IElement
        )
        self.assertFalse(block.is_empty)


class ImageEmptyMarker(zeit.content.article.testing.FunctionalTestCase, EmptyMarkerTest):
    block_type = 'image'

    def create_target(self):
        return self.repository['2006']['DSC00109_2.JPG']

    def set_reference(self, block, target):
        if target is None:
            block.references = target
        else:
            block.references = block.references.create(target)


class GalleryEmptyMarker(zeit.content.article.testing.FunctionalTestCase, EmptyMarkerTest):
    block_type = 'gallery'

    def create_target(self):
        from zeit.content.gallery.gallery import Gallery

        self.repository['gallery'] = Gallery()
        return self.repository['gallery']


class PortraitboxEmptyMarker(zeit.content.article.testing.FunctionalTestCase, EmptyMarkerTest):
    block_type = 'portraitbox'

    def create_target(self):
        from zeit.content.portraitbox.portraitbox import Portraitbox

        self.repository['portraitbox'] = Portraitbox()
        return self.repository['portraitbox']


class InfoboxEmptyMarker(zeit.content.article.testing.FunctionalTestCase, EmptyMarkerTest):
    block_type = 'infobox'

    def create_target(self):
        from zeit.content.infobox.infobox import Infobox

        self.repository['infobox'] = Infobox()
        return self.repository['infobox']
