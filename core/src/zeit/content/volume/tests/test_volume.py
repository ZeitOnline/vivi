from datetime import datetime
from zeit.cms.repository.folder import Folder
from zeit.content.volume.volume import Volume
import lxml.etree
import lxml.objectify
import mock
import pysolr
import pytz
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.content.cp.interfaces
import zeit.content.volume.interfaces
import zeit.content.volume.testing
import zeit.content.volume.volume


class TestVolumeCovers(zeit.content.volume.testing.FunctionalTestCase):

    def setUp(self):
        from zeit.content.image.testing import create_image_group
        super(TestVolumeCovers, self).setUp()
        self.repository['imagegroup'] = create_image_group()
        self.volume = Volume()

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


class TestVolume(zeit.content.volume.testing.FunctionalTestCase):

    def setUp(self):
        from zeit.cms.repository.folder import Folder
        from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
        from zeit.content.volume.volume import Volume
        super(TestVolume, self).setUp()
        volume = Volume()
        volume.year = 2015
        volume.volume = 1
        volume.product = zeit.cms.content.sources.Product(u'ZEI')
        self.repository['2015'] = Folder()
        self.repository['2015']['01'] = Folder()
        self.repository['2015']['01']['ausgabe'] = volume
        self.repository['2015']['01']['index'] = ExampleContentType()

    def test_looks_up_centerpage_from_product_setting(self):
        volume = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/2015/01/ausgabe')
        cp = zeit.content.cp.interfaces.ICenterPage(volume)
        self.assertEqual('http://xml.zeit.de/2015/01/index', cp.uniqueId)


class TestOrder(zeit.content.volume.testing.FunctionalTestCase):

    def setUp(self):
        super(TestOrder, self).setUp()
        self.create_volume(2015, 1)
        self.create_volume(2015, 2)

        self.solr = mock.Mock()
        self.zca.patch_utility(self.solr, zeit.solr.interfaces.ISolr)

    def create_volume(self, year, name):
        volume = Volume()
        volume.year = year
        volume.volume = name
        volume.product = zeit.cms.content.sources.Product(u'ZEI')
        volume.date_digital_published = datetime(
            year, name, 1, tzinfo=pytz.UTC)
        year = str(year)
        name = '%02d' % name
        self.repository[year] = Folder()
        self.repository[year][name] = Folder()
        self.repository[year][name]['ausgabe'] = volume

    def test_resolves_solr_result(self):
        self.solr.search.return_value = pysolr.Results(
            [{'uniqueId': 'http://xml.zeit.de/2015/02/ausgabe'}], 1)
        vol1 = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/2015/01/ausgabe')
        vol2 = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/2015/02/ausgabe')
        self.assertEqual(vol2, vol1.next)

    def test_no_solr_result_returns_None(self):
        self.solr.search.return_value = pysolr.Results([], 0)
        vol1 = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/2015/01/ausgabe')
        self.assertEqual(None, vol1.next)
        self.assertEqual(None, vol1.previous)

    def test_no_publish_date_returns_None(self):
        volume = Volume()
        year = 2015
        name = 1
        volume.year = year
        volume.volume = name
        volume.product = zeit.cms.content.sources.Product(u'ZEI')
        self.solr.search.return_value = pysolr.Results(
            [{'uniqueId': 'http://xml.zeit.de/2015/02/ausgabe'}], 1)
        self.assertEqual(None, volume.next)
        self.assertEqual(None, volume.previous)
