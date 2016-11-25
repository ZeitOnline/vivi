# -*- coding: utf-8 -*-
import mock
from ordereddict import OrderedDict
from collections import defaultdict

import lxml.etree

import zeit.cms.content.sources
from zeit.cms.repository.folder import Folder
import zeit.cms.testing
from zeit.content.article.testing import create_article
from zeit.content.volume.browser.toc import Toc, Excluder
from zeit.content.volume.volume import Volume
import zeit.content.volume.testing
import zeit.connector.mock


class TocFunctionalTest(zeit.content.volume.testing.FunctionalTestCase):

    def setUp(self):
        super(TocFunctionalTest, self).setUp()
        self.connector = zeit.connector.mock.connector_factory()
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

    def test_list_relevant_ressort_folders_returns_correct_directories(self):
        toc = Toc()
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
        foldernames = [tup[0] for tup in relevant_ressorts]
        self.assertIn('politik', foldernames)

    def test__get_all_product_ids_for_volume_zeit_product_id_found(self):
        t = Toc()
        ids = t._get_all_product_ids_for_volume()
        self.assertIn('ZEI', ids)

    def test_create_toc_element_from_xml_with_linebreak_in_teaser(self):
        article_xml = u"""
            <article>
                <head>
                    <attribute ns="http://namespaces.zeit.de/CMS/document"
                    name="page">20-20</attribute>
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

        expected = {'page': '20',
                    'title': 'Titel',
                    'teaser': 'Das soll der Teaser sein',
                    'author': 'Autor'}
        article_element = lxml.etree.fromstring(article_xml)
        toc = Toc()
        result = toc._create_toc_element(article_element)
        self.assertEqual(expected, result)

    def test_create_csv_with_all_values_is_exact(self):
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

    def test_create_csv_with_missing_values_in_toc_data(self):
        # Delete an author in input toc data
        product, ressort_dict = self.toc_data.iteritems().next()
        ressort, article_list = ressort_dict.iteritems().next()
        article_list[0]['author'] = ''
        input_data = {product: {ressort: article_list}}
        toc = Toc()
        assert toc.CSV_DELIMITER*2 in toc._create_csv(input_data)

    def test_product_source_has_zeit_product_id(self):
        t = Toc()
        volume = mock.Mock()
        volume.year = 2015
        volume.volume = 1
        t.context = volume
        mapping = t._create_product_id_full_name_mapping()
        self.assertEqual('Die Zeit'.lower(), mapping.get('ZEI', '').lower())

    def test_article_excluder_excludes_irrelevant_aritcles(self):
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


class TocBrowserTest(zeit.cms.testing.BrowserTestCase):
    layer = zeit.content.volume.testing.ZCML_LAYER

    def setUp(self):
        super(TocBrowserTest, self).setUp()
        volume = Volume()
        volume.year = 2015
        volume.volume = 1
        volume.product = zeit.cms.content.sources.Product(u'ZEI')
        self.article_title = 'Ein Test Titel'
        self.ressort_names = ['dossier', 'politik']
        self.article_page = 1
        with zeit.cms.testing.site(self.getRootFolder()):
            self.repository['ZEI'] = Folder()
            self.repository['ZEI']['2015'] = Folder()
            self.repository['ZEI']['2015']['01'] = Folder()
            self.repository['ZEI']['2015']['01']['ausgabe'] = volume
            for ressort_name in self.ressort_names:
                self.repository['ZEI']['2015']['01'][ressort_name] = Folder()
            with zeit.cms.testing.interaction():
                article = create_article()
                article.year = 2015
                article.volume = 1
                article.title = self.article_title
                article.page = self.article_page
                self.repository['ZEI']['2015']['01']['politik'][
                    'test_artikel'] = article

    def test_toc_generates_right_headers(self):
        b = self.browser
        b.handleErrors = False
        with mock.patch('zeit.content.volume.browser'
                        '.toc.Toc._create_toc_content') as create_content:
            create_content.return_value = 'some csv'
            b.open('http://localhost/++skin++vivi/repository/'
                   'ZEI/2015/01/ausgabe/@@toc.csv')
            self.assertEqual('text/csv', b.headers['content-type'])
            self.assertEqual('attachment; '
                             'filename="table_of_content_2015_01.csv"',
                             b.headers['content-disposition'])
            self.assertEllipsis("some csv", b.contents)

    def test_toc_generates_correct_csv(self):
        b = self.browser
        b.handleErrors = False
        b.open('http://localhost/++skin++vivi/repository/'
               'ZEI/2015/01/ausgabe/@@toc.csv')
        self.assertIn(self.article_title, b.contents)
        self.assertIn(str(self.article_page), b.contents)
        for ressort_name in self.ressort_names:
            self.assertIn(ressort_name.title(), b.contents)
        self.assertIn('DIE ZEIT'.lower(), b.contents.lower())
