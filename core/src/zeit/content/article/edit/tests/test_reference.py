# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest
import zeit.content.article.testing
import zope.lifecycleevent


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


class TestInfobox(ReferenceTest):

    @property
    def test_class(self):
        from zeit.content.article.edit.reference import Infobox
        return Infobox


class TestPortraitbox(ReferenceTest):

    @property
    def test_class(self):
        from zeit.content.article.edit.reference import Portraitbox
        return Portraitbox

    def test_default_layout_should_be_set(self):
        ref = self.get_ref()
        self.assertEquals('short', ref.xml.get('layout'))

    def test_layout_should_set_attribute(self):
        ref = self.get_ref()
        ref.layout = u'wide'
        self.assertEquals('wide', ref.xml.get('layout'))


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

    def test_infobox_factory(self):
        from zeit.content.article.edit.interfaces import IInfobox
        self.assert_factory('infobox', 'Infobox', IInfobox)

    def test_portraitbox_factory(self):
        from zeit.content.article.edit.interfaces import IPortraitbox
        self.assert_factory('portraitbox', 'Portraitbox', IPortraitbox)


class TestMetadataUpdate(zeit.content.article.testing.FunctionalTestCase):

    def assert_updated(self, referenced, factory_name):
        self.repository['refed'] = referenced
        #
        article = self.get_article()
        reference = self.get_factory(article, factory_name)()
        reference.references = self.repository['refed']
        self.repository['article'] = article

        #
        import zeit.workflow.interfaces
        import datetime
        import pytz
        workflow = zeit.workflow.interfaces.ITimeBasedPublishing(
            self.repository['refed'])
        workflow.release_period = (
            None, datetime.datetime(2005, 1, 2, tzinfo=pytz.UTC))

        #
        from zeit.cms.checkout.helper import checked_out
        with checked_out(self.repository['article']):
            pass
        self.assertEqual(
            u'2005-01-02T00:00:00+00:00',
            self.repository['article'].xml.body.division.getchildren()[0].get(
                'expires'))

    def test_gallery_metadata_should_be_updated(self):
        from zeit.content.gallery.gallery import Gallery
        self.assert_updated(Gallery(), 'gallery')

    def test_portraitbox_metadata_should_be_updated(self):
        from zeit.content.portraitbox.portraitbox import Portraitbox
        self.assert_updated(Portraitbox(), 'portraitbox')

    def test_infobox_metadata_should_be_updated(self):
        from zeit.content.infobox.infobox import Infobox
        self.assert_updated(Infobox(), 'infobox')

    def test_image_metadata_should_be_updated(self):
        self.assert_updated(self.repository['2006']['DSC00109_2.JPG'], 'image')


class EmptyMarkerTest(object):

    block_type = NotImplemented

    def create_block(self):
        return self.get_factory(self.get_article(), self.block_type)()

    def create_reference(self):
        raise NotImplementedError()

    def test_block_is_empty_after_creation(self):
        block = self.create_block()
        self.assertTrue(block.is_empty)

    def test_block_is_not_empty_after_setting_reference(self):
        block = self.create_block()
        block.references = self.create_reference()
        zope.lifecycleevent.modified(block)
        self.assertFalse(block.is_empty)

    def test_block_is_empty_after_removing_reference(self):
        block = self.create_block()
        block.references = self.create_reference()
        zope.lifecycleevent.modified(block)
        block.references = None
        zope.lifecycleevent.modified(block)
        self.assertTrue(block.is_empty)


class ImageEmptyMarker(zeit.content.article.testing.FunctionalTestCase,
                       EmptyMarkerTest):

    block_type = 'image'

    def create_reference(self):
        return self.repository['2006']['DSC00109_2.JPG']


class GalleryEmptyMarker(zeit.content.article.testing.FunctionalTestCase,
                         EmptyMarkerTest):

    block_type = 'gallery'

    def create_reference(self):
        from zeit.content.gallery.gallery import Gallery
        self.repository['gallery'] = Gallery()
        return self.repository['gallery']


class PortraitboxEmptyMarker(zeit.content.article.testing.FunctionalTestCase,
                             EmptyMarkerTest):

    block_type = 'portraitbox'

    def create_reference(self):
        from zeit.content.portraitbox.portraitbox import Portraitbox
        self.repository['portraitbox'] = Portraitbox()
        return self.repository['portraitbox']


class InfoboxEmptyMarker(zeit.content.article.testing.FunctionalTestCase,
                         EmptyMarkerTest):

    block_type = 'infobox'

    def create_reference(self):
        from zeit.content.infobox.infobox import Infobox
        self.repository['infobox'] = Infobox()
        return self.repository['infobox']
