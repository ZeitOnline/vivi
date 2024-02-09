# coding: utf-8
from datetime import datetime
from unittest import mock

import lxml.builder
import lxml.etree
import pytz
import requests_mock
import zope.app.appsetup.product
import zope.component

from zeit.cms.repository.folder import Folder
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.cms.workflow.interfaces import IPublicationDependencies
from zeit.content.image.testing import create_image_group
from zeit.content.volume.volume import Volume
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.cms.workflow.interfaces
import zeit.content.cp.centerpage
import zeit.content.cp.interfaces
import zeit.content.volume.interfaces
import zeit.content.volume.testing
import zeit.content.volume.volume
import zeit.find.interfaces


class TestVolumeCovers(zeit.content.volume.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.repository['imagegroup'] = create_image_group()
        self.cover = self.repository['imagegroup']
        self.volume = Volume()
        self.volume.product = zeit.cms.content.sources.Product('ZEI')

    def add_ipad_cover(self, product_id='ZEI'):
        node = lxml.builder.E.cover(
            href='http://xml.zeit.de/imagegroup/', id='ipad', product_id=product_id
        )
        self.volume.xml.find('covers').append(node)

    def test_set_raises_for_invalid_product(self):
        with self.assertRaises(ValueError):
            self.volume.set_cover('ipad', 'TEST', self.cover)

    def test_stores_uniqueId_in_xml_of_volume(self):
        self.volume.set_cover('ipad', 'ZEI', self.repository['imagegroup'])
        xml = self.volume.xml.find('covers/cover')
        self.assertEqual('ipad', xml.get('id'))
        self.assertEqual('ZEI', xml.get('product_id'))
        self.assertEqual('http://xml.zeit.de/imagegroup/', xml.get('href'))

    def test_deletes_existing_node_if_value_is_None(self):
        self.volume.set_cover('ipad', 'ZEI', self.repository['imagegroup'])
        self.volume.set_cover('ipad', 'ZEI', None)
        self.assertEqual(
            '<covers/>',
            zeit.cms.testing.xmltotext(self.volume.xml.find('covers')).strip(),
        )

    def test_raises_value_error_if_invalid_product_id_used_in_set_cover(self):
        with self.assertRaises(ValueError):
            self.volume.set_cover('ipad', 'TEST', self.repository['imagegroup'])

    def test_returns_none_if_invalid_product_id_used_in_get_cover(self):
        self.assertEqual(None, self.volume.get_cover('ipad', 'TEST'))

    def test_resolves_given_product_id(self):
        self.add_ipad_cover('ZMLB')
        self.assertEqual(self.cover, self.volume.get_cover('ipad', 'ZMLB'))

    def test_uses_product_of_volume_if_none_is_given(self):
        self.add_ipad_cover()
        self.assertEqual(self.cover, self.volume.get_cover('ipad'))

    def test_returns_main_product_if_no_dependent_cover_present(self):
        self.add_ipad_cover()
        self.assertEqual(self.cover, self.volume.get_cover('ipad', 'ZMLB'))


class TestReference(zeit.content.volume.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        volume = Volume()
        volume.year = 2015
        volume.volume = 1
        zeit.cms.content.add.find_or_create_folder('2015', '01')
        self.repository['2015']['01']['ausgabe'] = volume

    def test_content_with_missing_values_does_not_adapt_to_IVolume(self):
        with self.assertRaises(TypeError):
            zeit.content.volume.interfaces.IVolume(ExampleContentType())

    def test_content_with_year_and_volume_and_product_adapts_to_IVolume(self):
        content = ExampleContentType()
        content.year = 2015
        content.volume = 1
        content.product = zeit.cms.content.sources.Product('ZEI')
        volume = zeit.content.volume.interfaces.IVolume(content)
        self.assertEqual(volume, self.repository['2015']['01']['ausgabe'])

    def test_content_online_product_has_no_IVolume(self):
        # *All* content that is added in vivi gets year and volume from
        # zeit.cms.settings.interfaces.IGlobalSettings, so we need to ensure
        # that "online content" has no IVolume, only print content.
        # In addition we want only handle products with a location template
        # configured.
        content = ExampleContentType()
        content.year = 2015
        content.volume = 1
        content.product = zeit.cms.content.sources.Product('ZEDE')
        with self.assertRaises(TypeError):
            zeit.content.volume.interfaces.IVolume(content)

    def test_contents_with_defined_dependency_adapt_to_same_volume(self):
        zei_content = ExampleContentType()
        zei_content.year = 2015
        zei_content.volume = 1
        zei_content.product = zeit.cms.content.sources.Product('ZEI')
        zmlb_content = ExampleContentType()
        zmlb_content.year = 2015
        zmlb_content.volume = 1
        zmlb_content.product = zeit.cms.content.sources.Product('ZMLB')
        self.assertEqual(
            zeit.content.volume.interfaces.IVolume(zei_content),
            zeit.content.volume.interfaces.IVolume(zmlb_content),
        )

    def test_cant_adapt_content_with_dependency_defined_to_a_non_volume(self):
        zecw_content = ExampleContentType()
        zecw_content.year = 2015
        zecw_content.volume = 1
        zecw_content.product = zeit.cms.content.sources.Product('BADDEPENDENCY')
        with self.assertRaises(TypeError):
            zeit.content.volume.interfaces.IVolume(zecw_content)


class TestVolume(zeit.content.volume.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        volume = Volume()
        volume.year = 2015
        volume.volume = 1
        volume.product = zeit.cms.content.sources.Product('ZEI')
        self.repository['2015'] = Folder()
        self.repository['2015']['01'] = Folder()
        # Add a cover image-group
        self.repository['imagegroup'] = create_image_group()
        volume.set_cover('ipad', 'ZEI', self.repository['imagegroup'])
        self.repository['2015']['01']['ausgabe'] = volume

    def test_looks_up_centerpage_from_product_setting(self):
        self.repository['2015']['01']['index'] = zeit.content.cp.centerpage.CenterPage()
        volume = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2015/01/ausgabe')
        cp = zeit.content.cp.interfaces.ICenterPage(volume)
        self.assertEqual('http://xml.zeit.de/2015/01/index', cp.uniqueId)

    def test_non_cp_not_looked_up_for_centerpage(self):
        self.repository['2015']['01']['index'] = ExampleContentType()
        volume = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2015/01/ausgabe')
        cp = zeit.content.cp.interfaces.ICenterPage(volume, None)
        self.assertEqual(None, cp)

    def test_no_centerpage_setting_does_not_break(self):
        volume = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2015/01/ausgabe')
        with mock.patch(
            'zeit.content.volume.volume.Volume.product', new=mock.PropertyMock()
        ) as product:
            product().centerpage = None
            product().location = 'http://xml.zeit.de/{year}/{name}/ausgabe'
            cp = zeit.content.cp.interfaces.ICenterPage(volume, None)
        self.assertEqual(None, cp)

    def test_looks_up_centerpage_for_depent_product_content(self):
        content = ExampleContentType()
        content.product = zeit.cms.content.sources.Product('ZMLB')
        self.repository['2015']['01']['index'] = content
        volume = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2015/01/ausgabe')
        self.repository['2015']['01']['index'] = zeit.content.cp.centerpage.CenterPage()
        cp = zeit.content.cp.interfaces.ICenterPage(volume)
        self.assertEqual('http://xml.zeit.de/2015/01/index', cp.uniqueId)

    def test_no_teaserText_present_returns_default_string(self):
        volume = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2015/01/ausgabe')
        self.assertEqual('Teäser 01/2015', volume.teaserText)

    def test_covers_are_published_with_the_volume(self):
        volume = self.repository['2015']['01']['ausgabe']
        self.assertIn(
            self.repository['imagegroup'], IPublicationDependencies(volume).get_dependencies()
        )
        self.assertIn(
            self.repository['imagegroup'],
            IPublicationDependencies(volume).get_retract_dependencies(),
        )


class TestVolumeQueries(zeit.content.volume.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.create_volume(2015, 1)
        self.create_volume(2015, 2)
        self.elastic = mock.Mock()
        zope.component.getGlobalSiteManager().registerUtility(
            self.elastic, zeit.retresco.interfaces.IElasticsearch
        )
        zope.component.getGlobalSiteManager().registerUtility(
            self.elastic, zeit.find.interfaces.ICMSSearch
        )

    def create_volume(self, year, name):
        volume = Volume()
        volume.year = year
        volume.volume = name
        volume.product = zeit.cms.content.sources.Product('ZEI')
        volume.date_digital_published = datetime(year, name, 1, tzinfo=pytz.UTC)
        year = str(year)
        name = '%02d' % name
        self.repository[year] = Folder()
        self.repository[year][name] = Folder()
        self.repository[year][name]['ausgabe'] = volume

    def test_resolves_result(self):
        self.elastic.search.return_value = zeit.cms.interfaces.Result([{'url': '/2015/02/ausgabe'}])
        vol1 = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2015/01/ausgabe')
        vol2 = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2015/02/ausgabe')
        self.assertEqual(vol2, vol1.next)

    def test_no_result_returns_None(self):
        self.elastic.search.return_value = zeit.cms.interfaces.Result()
        vol1 = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2015/01/ausgabe')
        self.assertEqual(None, vol1.next)
        self.assertEqual(None, vol1.previous)

    def test_no_publish_date_returns_None(self):
        volume = Volume()
        year = 2015
        name = 1
        volume.year = year
        volume.volume = name
        volume.product = zeit.cms.content.sources.Product('ZEI')
        self.elastic.search.return_value = [{'url': '/2015/02/ausgabe'}]
        self.assertEqual(None, volume.next)
        self.assertEqual(None, volume.previous)

    def test_all_content_via_search_returns_empty_list_if_no_content(self):
        volume = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2015/01/ausgabe')
        self.elastic.search.return_value = zeit.cms.interfaces.Result()
        self.assertEqual(
            [],
            volume.all_content_via_search(additional_query_constraints=[{'term': {'foo': 'bar'}}]),
        )

    def test_all_content_via_search_returns_ICMS_content(self):
        volume = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2015/01/ausgabe')
        content = ExampleContentType()
        self.repository['2015']['01']['article'] = content
        self.elastic.search.return_value = zeit.cms.interfaces.Result([{'url': '/2015/01/article'}])
        self.assertListEqual(
            [content],
            volume.all_content_via_search(additional_query_constraints=[{'term': {'foo': 'bar'}}]),
        )

    @mock.patch(
        'zeit.content.volume.volume.' '_find_performing_articles_via_webtrekk', return_value='[]'
    )
    def test_all_volume_contents_should_change_access_value(self, mock):
        volume = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2015/01/ausgabe')
        repo = self.repository['2015']['01']
        content01 = ExampleContentType()
        content02 = ExampleContentType()
        content03 = ExampleContentType()
        repo['article01'] = content01
        repo['article02'] = content02
        repo['article03'] = content03

        # XXX We rely quite a bit on query structure here, but cannot test it.
        self.elastic.search.return_value = zeit.cms.interfaces.Result(
            [
                {'url': '/2015/01/article01'},
                {'url': '/2015/01/article02'},
                {'url': '/2015/01/article03'},
            ]
        )

        cnt = volume.all_content_via_search()
        for c in cnt:
            self.assertEqual('free', c.access)

        volume.change_contents_access('free', 'abo')
        for c in cnt:
            self.assertEqual('abo', c.access)

    @mock.patch(
        'zeit.content.volume.volume.' '_find_performing_articles_via_webtrekk', return_value='[]'
    )
    def test_volume_contents_access_dry_run_does_not_change_accces(self, mock):
        volume = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2015/01/ausgabe')
        repo = self.repository['2015']['01']
        content01 = ExampleContentType()
        repo['article01'] = content01

        self.elastic.search.return_value = zeit.cms.interfaces.Result(
            [
                {'url': '/2015/01/article01'},
            ]
        )

        cnt = volume.change_contents_access('free', 'abo', dry_run=True)

        self.assertEqual([content01], cnt)
        for c in cnt:
            self.assertEqual('free', c.access)


class TestWebtrekkQuery(TestVolumeQueries):
    def setUp(self):
        super().setUp()
        volume = Volume()
        volume.year = 2019
        volume.volume = 1
        info = zeit.cms.workflow.interfaces.IPublishInfo(volume)
        info.date_first_released = datetime(2019, 1, 1, tzinfo=pytz.UTC)
        self.volume = volume

    def webtrekk(self, resp):
        config = zope.app.appsetup.product.getProductConfiguration('zeit.content.volume')
        response = {'result': {'analysisData': resp}}
        m = requests_mock.Mocker()
        m.post(config['access-control-webtrekk-url'], status_code=200, json=response)
        return m

    def test_urls_are_filtered_according_to_config(self):
        webtrekk_data = [
            ['web..trekk|www.zeit.de/2019/01/foo', 1, 0.2],  # high cr
            ['web..trekk|www.zeit.de/2019/01/bar', 5, 0.01],  # high order
            ['web..trekk|www.zeit.de/2019/01/foobar', 5, 0.1],  # both
            ['web..trekk|www.zeit.de/2019/01/baz', 1, 0.01],  # None of above
        ]
        with self.webtrekk(webtrekk_data):
            res = zeit.content.volume.volume._find_performing_articles_via_webtrekk(self.volume)
            self.assertEqual({'/2019/01/foo', '/2019/01/bar', '/2019/01/foobar'}, set(res))

    def test_only_articles_of_given_volume_are_considered(self):
        webtrekk_data = [
            ['web..trekk|www.zeit.de/2019/01/foo', 10, 0.2],
            ['web..trekk|www.zeit.de/magazin/2019/01/bar', 10, 0.2],
            ['web..trekk|www.zeit.de/2019/02/bar', 10, 0.2],
        ]
        with self.webtrekk(webtrekk_data):
            res = zeit.content.volume.volume._find_performing_articles_via_webtrekk(self.volume)
            self.assertEqual({'/2019/01/foo', '/magazin/2019/01/bar'}, set(res))
