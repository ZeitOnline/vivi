import lxml.etree
import lxml.objectify
import zeit.cms.content.sources
import zeit.content.volume.interfaces
import zeit.content.volume.testing
import zeit.content.volume.volume


class TestVolumeCovers(zeit.content.volume.testing.FunctionalTestCase):

    def setUp(self):
        from zeit.content.image.testing import create_image_group
        super(TestVolumeCovers, self).setUp()
        self.repository['imagegroup'] = create_image_group()
        self.volume = zeit.content.volume.volume.Volume()

    def test_setattr_stores_uniqueId_in_XML_of_Volume(self):
        self.volume.covers['ipad'] = self.repository['imagegroup']
        self.assertEqual(
            '<covers xmlns:py="http://codespeak.net/lxml/objectify/pytype">'
            '<cover href="http://xml.zeit.de/imagegroup/" id="ipad"/>'
            '</covers>',
            lxml.etree.tostring(self.volume.xml.covers))

    def test_setattr_deletes_existing_node_if_value_is_None(self):
        self.volume.covers['ipad'] = self.repository['imagegroup']
        self.volume.covers['ipad'] = None
        self.assertEqual(
            '<covers xmlns:py="http://codespeak.net/lxml/objectify/pytype"/>',
            lxml.etree.tostring(self.volume.xml.covers))

    def test_getattr_retrieves_ICMSContent_via_uniqueId_in_XML_of_Volume(self):
        node = lxml.objectify.E.cover(
            href='http://xml.zeit.de/imagegroup/', id='ipad')
        lxml.objectify.deannotate(node[0], cleanup_namespaces=True)
        self.volume.xml.covers.append(node)

        self.assertEqual(
            self.repository['imagegroup'], self.volume.covers['ipad'])


class TestReference(zeit.content.volume.testing.FunctionalTestCase):

    def setUp(self):
        from zeit.cms.repository.folder import Folder
        from zeit.content.volume.volume import Volume
        super(TestReference, self).setUp()
        volume = Volume()
        volume.year = 2015
        volume.volume = 1
        self.repository['2015'] = Folder()
        self.repository['2015']['01'] = Folder()
        self.repository['2015']['01']['ausgabe'] = volume

    def test_content_with_missing_values_does_not_adapt_to_IVolume(self):
        from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
        with self.assertRaises(TypeError):
            zeit.content.volume.interfaces.IVolume(ExampleContentType())

    def test_content_with_year_and_volume_and_product_adapts_to_IVolume(self):
        from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
        content = ExampleContentType()
        content.year = 2015
        content.volume = 1
        content.product = zeit.cms.content.sources.Product(u'ZEI')
        volume = zeit.content.volume.interfaces.IVolume(content)
        self.assertEqual(
            volume,
            self.repository['2015']['01']['ausgabe'])

    def test_content_online_product_has_no_IVolume(self):
        # *All* content that is added in vivi gets year and volume from
        # zeit.cms.settings.interfaces.IGlobalSettings, so we need to ensure
        # that "online content" has no IVolume, only print content.
        # In addition we want only handle products with a location template
        # configured.
        from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
        content = ExampleContentType()
        content.year = 2015
        content.volume = 1
        content.product = zeit.cms.content.sources.Product(u'ZEDE')
        with self.assertRaises(TypeError):
            zeit.content.volume.interfaces.IVolume(content)
