# coding: utf-8
from unittest import mock

from pendulum import datetime
import lxml.builder
import lxml.etree
import pytest
import requests_mock
import zope.component

from zeit.cms.repository.folder import Folder
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.cms.workflow.interfaces import IPublicationDependencies, IPublishInfo
from zeit.content.article.article import Article
from zeit.content.article.interfaces import IArticle
from zeit.content.image.testing import create_image_group
from zeit.content.volume.volume import Volume
import zeit.cms.config
import zeit.cms.content.field
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
            href='http://xml.zeit.de/imagegroup', id='ipad', product_id=product_id
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
        self.assertEqual('http://xml.zeit.de/imagegroup', xml.get('href'))

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

    def test_no_volume_note_present_returns_default_string(self):
        volume = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2015/01/ausgabe')
        self.assertEqual('Teäser 01/2015', volume.volume_note)

    def test_covers_are_published_with_the_volume(self):
        volume = self.repository['2015']['01']['ausgabe']
        self.assertIn(
            self.repository['imagegroup'], IPublicationDependencies(volume).get_dependencies()
        )
        self.assertIn(
            self.repository['imagegroup'],
            IPublicationDependencies(volume).get_retract_dependencies(),
        )


@pytest.mark.parametrize(
    'color, raised_exception',
    [
        ('123456', None),  # Valid hex value
        ('abcdeg', zeit.cms.interfaces.ValidationError),  # Invalid hex (faulty character)
        ('ff12', zope.schema._bootstrapinterfaces.TooShort),  # Invalid hex value (too short)
        ('abcdef123456', zope.schema._bootstrapinterfaces.TooLong),  # Invalid hex value (too long)
        (None, None),  # Absent value raises nothing
    ],
)
def test_background_color_is_hex_validation(color, raised_exception):
    field = zeit.content.volume.interfaces.IVolume['background_color']
    if raised_exception:
        with pytest.raises(raised_exception):
            field.validate(color)
    else:
        field.validate(color)


class TestVolumeQueries(zeit.content.volume.testing.SQLTestCase):
    def create_volume(self, year, name, product='ZEI', published=True):
        volume = Volume()
        volume.year = year
        volume.volume = name
        volume.product = zeit.cms.content.sources.Product(product)
        if published:
            volume.date_digital_published = datetime(year, name, 1)
        year = str(year)
        name = '%02d' % name
        self.repository[year] = Folder()
        self.repository[year][name] = Folder()
        self.repository[year][name]['ausgabe'] = volume
        return self.repository[year][name]['ausgabe']

    def test_next_and_previous(self):
        vol1 = self.create_volume(2025, 1)
        magazin = self.create_volume(2025, 2, product='Dev')
        vol2 = self.create_volume(2025, 3)
        self.assertEqual(vol2, vol1.next)
        self.assertEqual(vol1, vol2.previous)
        self.assertEqual(None, magazin.next)
        self.assertEqual(None, magazin.previous)

    def test_no_results_if_no_other_volume_exist(self):
        vol1 = self.create_volume(2025, 1)
        self.assertEqual(None, vol1.next)
        self.assertEqual(None, vol1.previous)

    def test_unpublished_volumes_are_not_considered(self):
        vol1 = self.create_volume(2025, 1)
        self.create_volume(2025, 2, published=False)
        vol3 = self.create_volume(2025, 3)
        self.assertEqual(vol3, vol1.next)
        self.assertEqual(vol1, vol3.previous)


class TestVolumeAccessQueries(zeit.content.volume.testing.SQLTestCase):
    def setUp(self):
        super().setUp()
        self.create_volume(2025, 1)
        self.create_volume_content('2025', '01', 'article01')

    def create_volume_content(self, volume_year, volume_number, name, product='ZEI'):
        article = Article()
        zeit.cms.content.field.apply_default_values(article, IArticle)
        article.product = zeit.cms.content.sources.Product(product)
        article.volume = int(volume_number)
        article.year = int(volume_year)
        article.title = 'title'
        article.ressort = 'Kultur'
        article.access = 'free'
        info = IPublishInfo(article)
        info.published = True
        self.repository[volume_year][volume_number][name] = article
        return self.repository[volume_year][volume_number][name]

    def test_all_content_via_storage_returns_ICMS_content(self):
        volume = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2025/01/ausgabe')
        query = volume._query_content_for_current_volume()
        result = list(self.repository.search(query))
        self.assertEqual(
            [volume, zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2025/01/article01')],
            result,
        )

    def test_all_content_via_storage_returns_only_volume(self):
        volume = self.create_volume(2025, 2)
        query = volume._query_content_for_current_volume()
        result = list(self.repository.search(query))
        self.assertEqual(
            [volume],
            result,
        )

    @mock.patch(
        'zeit.content.volume.volume._find_performing_articles_via_webtrekk',
        return_value=[('/2025/01/', 'performingarticle')],
    )
    def test_all_volume_contents_should_change_access_value(self, mock):
        volume = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2025/01/ausgabe')
        self.create_volume_content('2025', '01', 'article02')
        self.create_volume_content('2025', '01', 'article03')
        query = volume._query_content_for_current_volume()
        cnt = list(self.repository.search(query))
        for c in cnt:
            if c.uniqueId != volume.uniqueId:
                self.assertEqual('free', c.access)

        volume.change_contents_access('free', 'abo')
        for c in cnt:
            if c.uniqueId != volume.uniqueId:
                self.assertEqual('abo', c.access)

    @mock.patch('pendulum.now', return_value=datetime(2025, 1, 2))
    def test_volume_published_days_ago(self, mock):
        volume = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2025/01/ausgabe')
        result = Volume.published_days_ago(1)
        self.assertEqual(volume, result)


class TestVolumeGetArticlesQuery(zeit.content.volume.testing.SQLTestCase):
    def setUp(self):
        super().setUp()
        self.create_volume(2025, 1)
        self.create_volume_content('2025', '01', 'article01')
        self.create_volume_content('2025', '01', 'article02', published=True, has_audio=True)

    def create_volume_content(
        self, volume_year, volume_number, name, product='ZEI', published=False, has_audio=False
    ):
        article = Article()
        zeit.cms.content.field.apply_default_values(article, IArticle)
        article.product = zeit.cms.content.sources.Product(product)
        article.volume = int(volume_number)
        article.year = int(volume_year)
        article.title = 'title'
        article.ressort = 'Kultur'
        article.access = 'free'
        article.has_audio = has_audio
        info = IPublishInfo(article)
        info.published = published
        self.repository[volume_year][volume_number][name] = article
        article = self.repository[volume_year][volume_number][name]
        info = IPublishInfo(article)
        info.urgent = True

    def test_volume_considers_unpublished_article(self):
        volume = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2025/01/ausgabe')
        result = list(volume.get_articles())
        self.assertIn(
            zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2025/01/article01'), result
        )

    def test_volume_considers_article_with_audio(self):
        volume = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2025/01/ausgabe')
        result = list(volume.get_articles())
        self.assertIn(
            zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2025/01/article02'), result
        )


class TestWebtrekkQuery(TestVolumeAccessQueries):
    def setUp(self):
        super().setUp()
        self.volume = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2025/01/ausgabe')

    def webtrekk(self, resp):
        webtrekk_url = zeit.cms.config.required(
            'zeit.content.volume', 'access-control-webtrekk-url'
        )
        response = {'result': {'analysisData': resp}}
        m = requests_mock.Mocker()
        m.post(webtrekk_url, status_code=200, json=response)
        return m

    def test_urls_are_filtered_according_to_config(self):
        webtrekk_data = [
            ['web..trekk|www.zeit.de/2025/01/foo', 1, 0.2],  # high cr
            ['web..trekk|www.zeit.de/2025/01/bar', 5, 0.01],  # high order
            ['web..trekk|www.zeit.de/2025/01/foobar', 5, 0.1],  # both
            ['web..trekk|www.zeit.de/2025/01/baz', 1, 0.01],  # None of above
        ]
        with self.webtrekk(webtrekk_data):
            res = zeit.content.volume.volume._find_performing_articles_via_webtrekk(self.volume)
            self.assertIn(('/2025/01', 'foo'), set(res))
            self.assertIn(('/2025/01', 'bar'), set(res))
            self.assertIn(('/2025/01', 'foobar'), set(res))
            self.assertNotIn(('/2025/01', 'bas'), set(res))

    def test_only_articles_of_given_volume_are_considered(self):
        webtrekk_data = [
            ['web..trekk|www.zeit.de/2025/01/foo', 10, 0.2],
            ['web..trekk|www.zeit.de/magazin/2025/01/bar', 10, 0.2],
            ['web..trekk|www.zeit.de/2025/02/bar', 10, 0.2],
        ]
        with self.webtrekk(webtrekk_data):
            res = zeit.content.volume.volume._find_performing_articles_via_webtrekk(self.volume)
            self.assertIn(('/2025/01', 'foo'), set(res))
            self.assertIn(('/magazin/2025/01', 'bar'), set(res))
            self.assertNotIn(('/2025/02', 'bas'), set(res))
