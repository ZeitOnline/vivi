import transaction

from zeit.cms.workflow.interfaces import IPublicationDependencies
import zeit.content.gallery.gallery


class TestEntryMetadata(zeit.content.gallery.testing.FunctionalTestCase):
    def test_gallery_entry_should_adapt_to_IImageMetadata(self):
        gallery = self.repository['gallery']
        entry = next(iter(gallery.values()))
        metadata = zeit.content.image.interfaces.IImageMetadata(entry)
        assert metadata.context is entry

    def test_gallery_entry_metadata_should_proxy_attributes(self):
        gallery = self.repository['gallery']
        entry = next(gallery.values())
        entry.title = 'Nice title'
        metadata = zeit.content.image.interfaces.IImageMetadata(entry)
        assert metadata.title == 'Nice title'

    def test_gallery_entry_metadata_should_overrule_attributes(self):
        gallery = self.repository['gallery']
        entry = next(gallery.values())
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
    def test_visible_entry_count_should_consider_layout(self):
        entries = {'01.jpg': None, '02.jpg': 'image-only', '03.jpg': 'hidden'}
        gallery = self.repository['gallery']
        for key, layout in entries.items():
            entry = gallery[key]
            entry.layout = layout
            gallery[key] = entry

        count = zeit.content.gallery.interfaces.IVisibleEntryCount(gallery)
        self.assertEqual(2, count)


class TestWorkflow(zeit.content.gallery.testing.FunctionalTestCase):
    def test_publishes_images_from_folder_with_gallery(self):
        gallery = self.repository['gallery']
        folder = self.repository['folder']
        pub = IPublicationDependencies(gallery)
        for deps in [pub.get_dependencies(), pub.get_retract_dependencies()]:
            self.assertIn(folder['01.jpg'], deps)

    def test_nonexistent_image_folder_does_not_break(self):
        folder = self.repository['folder']
        del folder.__parent__[folder.__name__]
        transaction.commit()
        gallery = self.repository['gallery']
        self.assertEqual([], IPublicationDependencies(gallery).get_dependencies())
