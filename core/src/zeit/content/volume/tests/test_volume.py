import lxml.etree
import lxml.objectify
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
        covers = zeit.content.volume.interfaces.IVolumeCovers(self.volume)
        covers.ipad = self.repository['imagegroup']
        self.assertEqual(
            '<cover xmlns:py="http://codespeak.net/lxml/objectify/pytype" '
            'id="ipad">http://xml.zeit.de/imagegroup/</cover>',
            lxml.etree.tostring(self.volume.xml.cover))

    def test_getattr_retrieves_ICMSContent_via_uniqueId_in_XML_of_Volume(self):
        node = lxml.objectify.E.cover(
            'http://xml.zeit.de/imagegroup/', id='ipad')
        lxml.objectify.deannotate(node[0], cleanup_namespaces=True)
        self.volume.xml.append(node)

        covers = zeit.content.volume.interfaces.IVolumeCovers(self.volume)
        self.assertEqual(self.repository['imagegroup'], covers.ipad)
