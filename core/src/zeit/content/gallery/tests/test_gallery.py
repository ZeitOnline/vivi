"""migrated from doctests in README.txt"""

import lxml.builder
import lxml.etree
import transaction
import zope.component
import zope.event
import zope.index.text.interfaces
import zope.interface.verify
import zope.lifecycleevent

from zeit.cms.repository.folder import Folder
from zeit.cms.workflow.interfaces import IPublicationDependencies
from zeit.content.image.testing import create_image
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.content.gallery.gallery
import zeit.content.gallery.interfaces
import zeit.content.gallery.testing
import zeit.content.image.interfaces


class TestEntryMetadata(zeit.content.gallery.testing.FunctionalTestCase):
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


class TestBasicGalleryFunctionality(zeit.content.gallery.testing.FunctionalTestCase):
    def test_empty_gallery_has_zero_length(self):
        gallery = zeit.content.gallery.gallery.Gallery()
        self.assertEqual(0, len(gallery))

    def test_gallery_provides_IGallery_interface(self):
        gallery = zeit.content.gallery.gallery.Gallery()
        self.assertTrue(
            zope.interface.verify.verifyObject(zeit.content.gallery.interfaces.IGallery, gallery)
        )

    def test_gallery_provides_IEditorialContent_interface(self):
        gallery = zeit.content.gallery.gallery.Gallery()
        self.assertTrue(
            zope.interface.verify.verifyObject(zeit.cms.interfaces.IEditorialContent, gallery)
        )

    def test_assign_image_folder_updates_gallery_length(self):
        gallery = zeit.content.gallery.gallery.Gallery()
        repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
        repository['folder'] = Folder()
        zeit.content.gallery.testing.add_image('folder', '01.jpg')
        zeit.content.gallery.testing.add_image('folder', '02.jpg')
        transaction.commit()

        gallery.image_folder = repository['folder']
        self.assertEqual(2, len(gallery))
        self.assertEqual(['01.jpg', '02.jpg'], list(gallery.keys()))


class TestImageFolderManagement(zeit.content.gallery.testing.FunctionalTestCase):
    def test_adding_image_requires_reload(self):
        initial_keys = list(self.gallery.keys())
        self.assertEqual(['01.jpg', '02.jpg'], initial_keys)

        zeit.content.gallery.testing.add_image('folder', '03.jpg')
        transaction.commit()

        self.assertEqual(initial_keys, list(self.gallery.keys()))

        self.gallery.reload_image_folder()
        self.assertEqual(['01.jpg', '02.jpg', '03.jpg'], list(self.gallery.keys()))

    def test_gallery_xml_reflects_image_folder(self):
        self.gallery.reload_image_folder()
        xml_text = zeit.cms.testing.xmltotext(self.gallery.xml)
        self.assertIn('<image-folder>http://xml.zeit.de/folder</image-folder>', xml_text)
        self.assertIn('src="http://xml.zeit.de/folder/01.jpg"', xml_text)


class TestGalleryEntryDetails(zeit.content.gallery.testing.FunctionalTestCase):
    def test_gallery_entry_creation(self):
        entry = self.gallery['01.jpg']
        self.assertIsInstance(entry, zeit.content.gallery.gallery.GalleryEntry)
        self.assertEqual('http://xml.zeit.de/folder/01.jpg', entry.image.uniqueId)

    def test_entry_initial_state(self):
        entry = self.gallery['01.jpg']
        self.assertIsNone(entry.title)
        self.assertIsNone(entry.text.text)
        self.assertEqual('Nice image', entry.caption)

    def test_entry_modification_requires_reassignment(self):
        entry = self.gallery['01.jpg']
        entry.text = lxml.builder.E.text(lxml.builder.E.p('Seit zwei Uhr in der Früh'))
        entry.caption = 'Gallery & caption'

        xml_text = zeit.cms.testing.xmltotext(self.gallery.xml)
        self.assertIn('<caption>Nice image</caption>', xml_text)

        self.gallery['01.jpg'] = entry
        xml_text = zeit.cms.testing.xmltotext(self.gallery.xml)
        self.assertIn('<caption>Gallery &amp; caption</caption>', xml_text)
        self.assertIn('<p>Seit zwei Uhr in der Früh</p>', xml_text)

    def test_object_modified_event_updates_gallery(self):
        entry = self.gallery['01.jpg']
        entry.title = 'Der Wecker klingelt'
        zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(entry))

        xml_text = zeit.cms.testing.xmltotext(self.gallery.xml)
        self.assertIn('<title>Der Wecker klingelt</title>', xml_text)

    def test_entry_data_persistence(self):
        entry = self.gallery['01.jpg']
        entry.title = 'Der Wecker klingelt'
        entry.text = lxml.builder.E.text(lxml.builder.E.p('Seit zwei Uhr in der Früh'))
        entry.caption = 'Gallery & caption'
        self.gallery['01.jpg'] = entry

        entry = self.gallery['01.jpg']
        self.assertEqual('Der Wecker klingelt', entry.title)
        self.assertEqual('Seit zwei Uhr in der Fr\xfch', entry.text.find('p').text)
        self.assertEqual('Gallery & caption', entry.caption)


class TestEntryLayout(zeit.content.gallery.testing.FunctionalTestCase):
    def test_layout_vocabulary(self):
        field = zeit.content.gallery.interfaces.IGalleryEntry['layout']
        self.assertEqual(['hidden', 'image-only'], sorted(list(field.vocabulary)))

    def test_entry_layout_default_is_none(self):
        entry = self.gallery['01.jpg']
        self.assertIsNone(entry.layout)

    def test_set_layout_reflects_in_xml(self):
        entry = self.gallery['01.jpg']
        entry.layout = 'image-only'
        self.gallery['01.jpg'] = entry

        xml_text = zeit.cms.testing.xmltotext(self.gallery.xml)
        self.assertIn('layout="image-only"', xml_text)

    def test_set_layout_to_none_removes_attribute(self):
        entry = self.gallery['01.jpg']
        entry.layout = 'image-only'
        self.gallery['01.jpg'] = entry

        entry = self.gallery['01.jpg']
        self.assertEqual('image-only', entry.layout)

        entry.layout = None
        self.gallery['01.jpg'] = entry

        xml_text = zeit.cms.testing.xmltotext(self.gallery.xml)
        self.assertNotIn('layout="image-only"', xml_text)

    def test_entry_crops_initially_empty(self):
        entry = self.gallery['01.jpg']
        self.assertEqual([], entry.crops)

    def test_crops_relationship(self):
        zeit.content.gallery.testing.add_image('folder', '02.jpg', '01.jpg-10x10.jpg')
        transaction.commit()
        self.gallery.reload_image_folder()

        crop_entry = self.gallery['01.jpg-10x10.jpg']
        crop_entry.is_crop_of = '01.jpg'
        self.gallery['01.jpg-10x10.jpg'] = crop_entry

        # Original entry should now list the crop
        entry = self.gallery['01.jpg']
        self.assertEqual('01.jpg-10x10.jpg', entry.crops[0].__name__)

    def test_is_crop_of_property(self):
        entry = self.gallery['01.jpg']
        self.assertIsNone(entry.is_crop_of)

        entry.is_crop_of = 'foo'
        self.gallery['01.jpg'] = entry

        entry = self.gallery['01.jpg']
        self.assertEqual('foo', entry.is_crop_of)

        # Reset to None
        entry.is_crop_of = None
        self.gallery['01.jpg'] = entry
        self.assertIsNone(self.gallery['01.jpg'].is_crop_of)

    def test_sorting_initial_order(self):
        self.assertEqual(['01.jpg', '02.jpg'], list(self.gallery.keys()))

    def test_sorting_update_order(self):
        self.gallery.updateOrder(['02.jpg', '01.jpg'])
        self.assertEqual(['02.jpg', '01.jpg'], list(self.gallery.keys()))

        # Verify XML reflects new order
        xml_text = zeit.cms.testing.xmltotext(self.gallery.xml)
        blocks = xml_text.split('<block name="')
        # First match after split would be empty, second would be '02.jpg'
        self.assertTrue(blocks[1].startswith('02.jpg'))

    def test_sorting_update_order_validates_keys(self):
        with self.assertRaises(ValueError) as cm:
            self.gallery.updateOrder(['01.jpg'])
        self.assertIn('same keys as the container', str(cm.exception))

    def test_sorting_restore_original_order(self):
        self.gallery.updateOrder(['02.jpg', '01.jpg'])
        self.gallery.updateOrder(['01.jpg', '02.jpg'])
        self.assertEqual(['01.jpg', '02.jpg'], list(self.gallery.keys()))

    def test_container_contains(self):
        self.assertIn('01.jpg', self.gallery)
        self.assertNotIn('"foo]"', self.gallery)

    def test_container_get(self):
        entry = self.gallery.get('01.jpg')
        self.assertIsInstance(entry, zeit.content.gallery.gallery.GalleryEntry)
        self.assertIsNone(self.gallery.get('":F34'))

    def test_container_items(self):
        items = list(self.gallery.items())
        self.assertEqual(2, len(items))
        names, entries = zip(*items)
        self.assertEqual(('01.jpg', '02.jpg'), names)
        for entry in entries:
            self.assertIsInstance(entry, zeit.content.gallery.gallery.GalleryEntry)

    def test_container_values(self):
        values = list(self.gallery.values())
        self.assertEqual(2, len(values))
        for entry in values:
            self.assertIsInstance(entry, zeit.content.gallery.gallery.GalleryEntry)

    def test_container_iter(self):
        keys = []
        for name in self.gallery:
            keys.append(name)
        self.assertEqual(['01.jpg', '02.jpg'], keys)

    def test_removed_image_not_in_keys(self):
        del self.repository['folder']['01.jpg']
        transaction.commit()

        self.assertEqual(['02.jpg'], list(self.gallery.keys()))

    def test_removed_image_raises_keyerror(self):
        del self.repository['folder']['01.jpg']
        transaction.commit()

        with self.assertRaises(KeyError):
            self.gallery['01.jpg']

    def test_reload_removes_deleted_image_from_xml(self):
        xml_text = zeit.cms.testing.xmltotext(self.gallery.xml)
        self.assertIn('name="01.jpg"', xml_text)

        del self.repository['folder']['01.jpg']
        transaction.commit()
        self.gallery.reload_image_folder()

        xml_text = zeit.cms.testing.xmltotext(self.gallery.xml)
        self.assertNotIn('name="01.jpg"', xml_text)

    def test_thumbnail_cleanup(self):
        initial_thumbnails = self.repository['folder']['thumbnails'].keys()
        self.assertIn('01.jpg', initial_thumbnails)

        del self.repository['folder']['01.jpg']
        transaction.commit()
        self.gallery.reload_image_folder()

        remaining_thumbnails = self.repository['folder']['thumbnails'].keys()
        self.assertEqual(['02.jpg'], list(remaining_thumbnails))

    def test_empty_caption_regression(self):
        """Test that empty caption tags don't break the system"""
        # Add empty caption tag manually (regression test)
        self.gallery.xml.xpath('body/column[2]/container/block')[0].append(lxml.builder.E.caption())
        # Should not raise an exception
        values = list(self.gallery.values())
        self.assertTrue(len(values) > 0)


class TestSearchableText(zeit.content.gallery.testing.FunctionalTestCase):
    def test_searchable_text_adapter(self):
        self.gallery.xml = lxml.etree.fromstring("""\
            <gallery>
              <head>
              </head>
              <body>
                <column layout="left"/>
                <column layout="right">
                  <container>
                    <block>
                      <text>
                         foo bar
                      </text>
                      <image expires="2007-04-09" src="http://xml.zeit.de/folder/01.jpg"
                            width="380" align="left">
                        <copyright>© Martin Rose/Getty Images</copyright>
                        BILD
                      </image>
                    </block>
                  </container>
                </column>
              </body>
            </gallery>""")
        self.gallery.reload_image_folder()
        adapter = zope.index.text.interfaces.ISearchableText(self.gallery)
        searchable_text = adapter.getSearchableText()
        self.assertIsInstance(searchable_text, list)
        text_content = searchable_text[0]
        self.assertIn('foo bar', text_content)
