import transaction
import zope.component

from zeit.cms.repository.folder import Folder
from zeit.cms.workflow.interfaces import IPublicationDependencies
from zeit.content.image.testing import create_image
import zeit.content.gallery.gallery


class TestEntryMetadata(zeit.content.gallery.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        gallery = zeit.content.gallery.gallery.Gallery()
        repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
        repository['folder'] = Folder()
        gallery.image_folder = repository['folder']
        zeit.content.gallery.testing.add_image('folder', '01.jpg')
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
        super().setUp()
        gallery = zeit.content.gallery.gallery.Gallery()
        repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
        self.repository['folder'] = Folder()
        gallery.image_folder = repository['folder']
        entries = {'01.jpg': None, '02.jpg': 'image-only', '03.jpg': 'hidden'}
        for key in entries:
            zeit.content.gallery.testing.add_image('folder', key)
        transaction.commit()
        gallery.reload_image_folder()
        for key, layout in entries.items():
            entry = gallery[key]
            entry.layout = layout
            gallery[key] = entry
        self.gallery = gallery

    def test_visible_entry_count_should_consider_layout(self):
        count = zeit.content.gallery.interfaces.IVisibleEntryCount(self.gallery)
        self.assertEqual(2, count)


class TestWorkflow(zeit.content.gallery.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.folder = self.repository['image-folder'] = Folder()
        image = create_image('opernball.jpg')
        image = self.folder['opernball.jpg'] = image

        gallery = zeit.content.gallery.gallery.Gallery()
        gallery.image_folder = self.folder
        self.gallery = self.repository['gallery'] = gallery
        transaction.commit()

    def test_publishes_images_from_folder_with_gallery(self):
        pub = IPublicationDependencies(self.gallery)
        for deps in [pub.get_dependencies(), pub.get_retract_dependencies()]:
            self.assertIn(self.folder['opernball.jpg'], deps)

    def test_nonexistent_image_folder_does_not_break(self):
        del self.folder.__parent__[self.folder.__name__]
        transaction.commit()
        self.assertEqual([], IPublicationDependencies(self.gallery).get_dependencies())
