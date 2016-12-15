# -*- coding: utf-8 -*-
import sys
import mock
from ordereddict import OrderedDict
from collections import defaultdict

import lxml.etree

import zope.component

import zeit.cms.content.sources
import zeit.cms.content.add
from zeit.cms.repository.folder import Folder
import zeit.cms.testing
import zeit.connector.mock
from zeit.content.article.testing import create_article
import zeit.content.volume.interfaces
from zeit.content.volume.browser.toc import Toc, Excluder
from zeit.content.volume.volume import Volume
import zeit.content.volume.testing


class TocFunctionalTest(zeit.content.volume.testing.FunctionalTestCase):

    def setUp(self):
        super(TocFunctionalTest, self).setUp()
        self.toc_data = OrderedDict()
        self.toc_data['Die Zeit'] = OrderedDict(
            {'Politik': [{'page': '1',
                          'title': 'title',
                          'teaser': 'tease',
                          'author': 'Autor'}]
             }
        )
        self.toc_data['Anderer'] = OrderedDict(
            {'Dossier': [
                {'page': '1',
                 'title': 'title',
                 'teaser': 'tease',
                 'author': 'Autor'},
                {'page': '3',
                 'title': 'title2',
                 'teaser': 'tease',
                 'author': 'Autor'}
            ]}
        )
        self.article_xml_template = u"""
            <article>
                <head>
                    <attribute ns="http://namespaces.zeit.de/CMS/document"
                    name="page">{page}</attribute>
                    <attribute ns="http://namespaces.zeit.de/CMS/document"
                    name="author">Autor</attribute>
                </head>
                <body>
                     <title>Titel</title>
                     <subtitle>Das soll der Teaser
                     sein</subtitle>
                </body>
            </article>
        """

    def test_list_relevant_ressort_folders_excludes_leserbriefe_and_images(
            self):
        toc = Toc()
        toc_connector = zope.component.getUtility(
            zeit.content.volume.interfaces.ITocConnector)
        self.zca.patch_utility(toc_connector,
                               zeit.connector.interfaces.IConnector)
        folders = ['images', 'leserbriefe', 'politik']
        with zeit.cms.testing.site(self.getRootFolder()):
            self.repository['ZEI'] = Folder()
            self.repository['ZEI']['2015'] = Folder()
            self.repository['ZEI']['2015']['01'] = Folder()
            for foldername in folders:
                self.repository['ZEI']['2015']['01'][foldername] = Folder()
            relevant_ressorts = toc.list_relevant_ressort_folders(
                'http://xml.zeit.de'
                '/ZEI/2015/01')
        foldernames = [folder.__name__ for folder in relevant_ressorts]
        self.assertIn('politik', foldernames)
        self.zca.reset()

    def test_create_toc_element_should_flatten_linebreaks(self):
        article_xml = self.article_xml_template.format(page='20-20')
        expected = {'page': 20,
                    'title': 'Titel',
                    'teaser': 'Das soll der Teaser sein',
                    'author': 'Autor'}
        article_element = lxml.etree.fromstring(article_xml)
        toc = Toc()
        result = toc._create_toc_element(article_element)
        self.assertEqual(expected, result)

    def test_csv_is_created_from_toc_data(self):
        expected = """Die Zeit\r
Politik\r
1\tAutor\ttitle tease\r
Anderer\r
Dossier\r
1\tAutor\ttitle tease\r
3\tAutor\ttitle2 tease\r
"""
        toc = Toc()
        res = toc._create_csv(self.toc_data)
        self.assertEqual(expected, res)

    def test_create_csv_with_missing_toc_value_has_empty_field(self):
        # Delete an author in input toc data
        product, ressort_dict = self.toc_data.iteritems().next()
        ressort, article_list = ressort_dict.iteritems().next()
        article_list[0]['author'] = ''
        input_data = {product: {ressort: article_list}}
        toc = Toc()
        assert toc.CSV_DELIMITER*2 in toc._create_csv(input_data)

    def test_empty_page_node_in_xml_results_in_max_int_page_in_toc_entry(self):
        article_xml = self.article_xml_template.format(page='')
        article_element = lxml.etree.fromstring(article_xml)
        t = Toc()
        entry = t._create_toc_element(article_element)
        assert sys.maxint == entry.get('page')

    def test_product_id_mapping_has_full_name_for_zei_product_id(self):
        t = Toc()
        volume = mock.Mock()
        volume.year = 2015
        volume.volume = 1
        t.context = volume
        mapping = t._create_product_id_full_name_mapping()
        self.assertEqual('Die Zeit'.lower(), mapping.get('ZEI', '').lower())

    def test_sorts_entries_with_max_int_page_as_last_toc_element(self):
        toc_data = {
            'Die Zeit': {
                'Politik':
                    [
                        {'page': sys.maxint, 'title': 'title2'},
                        {'page': 1, 'title': 'title1'}
                    ]
            }
        }
        toc_data = OrderedDict(toc_data)
        t = Toc()
        result = t._sort_toc_data(toc_data)
        assert sys.maxint == result.get('Die Zeit').get('Politik')[-1].get(
            'page')

    def test_article_excluder_excludes_blacklisted_property_values(self):
        excluder = Excluder()
        xml_template = u"""
        <article>
            <head>
                <attribute ns="http://namespaces.zeit.de/CMS/document"
                name="jobname">{d[jobname]}</attribute>
            </head>
            <body>
                 <title>{d[title]}</title>
                 <supertitle>{d[supertitle]}</supertitle>
            </body>
        </article>
        """
        for values in [{'title': u'Heute 20.02.2016'},
                       {'supertitle': u'WIR RATEN AB'},
                       {'jobname': u'AS-Zahl'}]:
            xml = xml_template.format(d=defaultdict(str, **values))
            self.assertEqual(False,
                             excluder.is_relevant(lxml.etree.fromstring(xml)))

    def test_init_toc_connector_is_registered_as_connector(self):
        old_connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        # register_archive_connector is called in __init__
        # check for the correct side effects
        t = Toc()
        new_connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        # Check if a new IConnector was registered
        assert old_connector is not new_connector
        # Check if the toc.connector is the ITocConnector
        assert t.connector is zope.component.getUtility(
            zeit.content.volume.interfaces.ITocConnector)
        assert t.connector is zope.component.getUtility(
            zeit.connector.interfaces.IConnector)


class TocBrowserTest(zeit.cms.testing.BrowserTestCase):
    layer = zeit.content.volume.testing.ZCML_LAYER

    def setUp(self):
        super(TocBrowserTest, self).setUp()
        # Create the volume object with the mock IConnector
        volume = Volume()
        volume.year = 2015
        volume.volume = 1
        volume.product = zeit.cms.content.sources.Product(u'ZEI')
        self.article_title = 'Ein Test Titel'
        self.ressort_names = ['dossier', 'politik']
        self.article_page = 1
        with zeit.cms.testing.site(self.getRootFolder()):
            zeit.cms.content.add.find_or_create_folder('2015', '01')
            self.repository['2015']['01']['ausgabe'] = volume
        # Now use the mock ITocConnector to mock the archive folders and the
        # article
        toc_connector = zope.component.getUtility(
            zeit.content.volume.interfaces.ITocConnector)
        self.zca.patch_utility(toc_connector,
                               zeit.connector.interfaces.IConnector)
        with zeit.cms.testing.site(self.getRootFolder()):
            for ressort_name in self.ressort_names:
                zeit.cms.content.add.find_or_create_folder('ZEI', '2015',
                                                           '01', ressort_name)
            with zeit.cms.testing.interaction():
                article = create_article()
                article.year = 2015
                article.volume = 1
                article.title = self.article_title
                article.page = self.article_page
                self.repository['ZEI']['2015']['01']['politik'][
                    'test_artikel'] = article
        self.zca.reset()

    def test_toc_view_is_csv_file_download(self):
        b = self.browser
        with mock.patch('zeit.content.volume.browser'
                        '.toc.Toc._create_toc_content') as create_content:
            create_content.return_value = 'some csv'
            b.open('http://localhost/++skin++vivi/repository/'
                   '2015/01/ausgabe/@@toc.csv')
            self.assertEqual('text/csv', b.headers['content-type'])
            self.assertEqual('attachment; '
                             'filename="table_of_content_2015_01.csv"',
                             b.headers['content-disposition'])
            self.assertEllipsis("some csv", b.contents)

    def test_toc_generates_csv(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/'
               '2015/01/ausgabe/@@toc.csv')
        self.assertIn(self.article_title, b.contents)
        self.assertIn(str(self.article_page), b.contents)
        for ressort_name in self.ressort_names:
            self.assertIn(ressort_name.title(), b.contents)
        self.assertIn('DIE ZEIT'.lower(), b.contents.lower())
