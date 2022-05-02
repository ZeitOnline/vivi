import transaction
import unittest
import zeit.content.gallery.gallery
import zope.component


class TestHTMLContent(unittest.TestCase):

    def test_get_tree_should_append_text(self):
        gallery = zeit.content.gallery.gallery.Gallery()
        html = zeit.content.gallery.gallery.HTMLContent(gallery)
        tree = html.get_tree()
        self.assertEqual('text', tree.tag)
        self.assertEqual(1, len(gallery.xml.body.findall('text')))

    def test_get_tree_should_return_existing_text(self):
        gallery = zeit.content.gallery.gallery.Gallery()
        gallery.xml.body['text'] = 'honk'
        html = zeit.content.gallery.gallery.HTMLContent(gallery)
        tree = html.get_tree()
        self.assertEqual('text', tree.tag)
        self.assertEqual('honk', tree.text)
        self.assertEqual(1, len(gallery.xml.body.findall('text')))


class TestEntryMetadata(zeit.content.gallery.testing.FunctionalTestCase):

    def setUp(self):
        super(TestEntryMetadata, self).setUp()
        gallery = zeit.content.gallery.gallery.Gallery()
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        gallery.image_folder = repository['2007']
        zeit.content.gallery.testing.add_image('2007', '01.jpg')
        transaction.commit()
        gallery.reload_image_folder()
        self.gallery = gallery

    def test_gallery_entry_should_adapt_to_IImageMetadata(self):
        entry = next(iter(self.gallery.values()))
        metadata = zeit.content.image.interfaces.IImageMetadata(entry)
        assert metadata.context is entry

    def test_gallery_entry_metadata_should_proxy_attributes(self):
        entry = next(self.gallery.values())
        entry.title = 'Nice title'
        metadata = zeit.content.image.interfaces.IImageMetadata(entry)
        assert metadata.title == 'Nice title'

    def test_gallery_entry_metadata_should_overrule_attributes(self):
        entry = next(self.gallery.values())
        entry.title = 'Nice title'
        metadata = zeit.content.image.interfaces.IImageMetadata(entry)
        metadata.title = 'Beautiful title'
        assert metadata.title == 'Beautiful title'


class TestEntryImages(zeit.content.gallery.testing.FunctionalTestCase):

    def test_gallery_entry_should_adapt_to_IImages(self):
        entry = zeit.content.gallery.gallery.GalleryEntry()
        entry.image = object()
        images = zeit.content.image.interfaces.IImages(entry)
        assert hasattr(images, 'fill_color')
        assert images.image is entry.image


class TestVisibleEntryCount(zeit.content.gallery.testing.FunctionalTestCase):

    def setUp(self):
        super(TestVisibleEntryCount, self).setUp()
        gallery = zeit.content.gallery.gallery.Gallery()
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        gallery.image_folder = repository['2007']
        entries = {'01.jpg': None, '02.jpg': 'image-only', '03.jpg': 'hidden'}
        for key in entries:
            zeit.content.gallery.testing.add_image('2007', key)
        transaction.commit()
        gallery.reload_image_folder()
        for key, layout in entries.items():
            entry = gallery[key]
            entry.layout = layout
            gallery[key] = entry
        self.gallery = gallery

    def test_visible_entry_count_should_consider_layout(self):
        count = zeit.content.gallery.interfaces.IVisibleEntryCount(
            self.gallery)
        self.assertEqual(2, count)
