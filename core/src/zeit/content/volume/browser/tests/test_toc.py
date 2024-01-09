# -*- coding: utf-8 -*-
# ruff: noqa: E501
from collections import OrderedDict
from io import StringIO
from unittest import mock
import sys

from zeit.content.article.article import Article
from zeit.content.article.testing import create_article
from zeit.content.author.author import Author
from zeit.content.volume.browser.toc import Toc
from zeit.content.volume.volume import Volume
import zeit.cms.content.add
import zeit.cms.content.sources
import zeit.cms.testing
import zeit.content.volume.interfaces
import zeit.content.volume.testing


class TocFunctionalTest(zeit.content.volume.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.toc_data = OrderedDict()
        self.toc_data['Die Zeit'] = OrderedDict(
            {
                'Politik': [
                    {
                        'page': '1',
                        'title': 'title',
                        'teaser': 'tease',
                        'access': 'frei verfügbar',
                        'authors': 'Helmut Schmidt',
                        'volume': '1',
                        'year': '2015',
                        'supertitle': 'Super',
                        'article_id': '1234567',
                    }
                ]
            }
        )
        self.toc_data['Anderer'] = OrderedDict(
            {
                'Dossier': [
                    {
                        'page': '1',
                        'access': 'frei verfügbar',
                        'authors': 'Helmut Kohl',
                        'title': 'title',
                        'teaser': 'tease',
                        'supertitle': 'Super',
                        'volume': '1',
                        'year': '2015',
                        'article_id': '0123456',
                    },
                    {
                        'page': '3',
                        'access': 'frei verfügbar',
                        'authors': 'Helmut Schmidt, Helmut Kohl',
                        'title': 'title2',
                        'teaser': 'tease',
                        'volume': '1',
                        'year': '2015',
                        'supertitle': 'Super',
                        'article_id': '0123456',
                    },
                ]
            }
        )
        author = Author()
        author.firstname = 'Helmut'
        author.lastname = 'Schmidt'
        self.repository['author'] = author
        self.article_xml_template = """
            <article>
                <head>
                    <attribute ns="http://namespaces.zeit.de/CMS/document"
                    name="page">{page}</attribute>
                    <attribute ns="http://namespaces.zeit.de/CMS/document"
                    name="access">free</attribute>
                    <attribute ns="http://namespaces.zeit.de/CMS/interred"
                    name="article_id">0123456</attribute>
                    <author href="http://xml.zeit.de/author"/>
                </head>
                <body>
                     <title>Titel</title>
                     <subtitle>Das soll der Teaser sein</subtitle>
                </body>
            </article>
        """

    def test_create_toc_element_should_flatten_linebreaks(self):
        article = Article(StringIO(self.article_xml_template.format(page='20')))
        self.repository['article'] = article
        article.updateDAVFromXML()
        expected = {
            'page': 20,
            'title': 'Titel',
            'teaser': 'Das soll der Teaser sein',
            'supertitle': '',
            'access': 'frei verfügbar',
            'authors': 'Helmut Schmidt',
            'article_id': '0123456',
        }
        toc = Toc(mock.Mock(), mock.Mock())
        result = toc._create_toc_element(article)
        self.assertEqual(expected, result)

    def test_csv_is_created_from_toc_data(self):
        expected = """1\ttitle tease\t\t\tfrei verfügbar\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tPolitik\t2015\t1\tDie Zeit\tHelmut Schmidt\t1234567\r
1\ttitle tease\t\t\tfrei verfügbar\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tDossier\t2015\t1\tAnderer\tHelmut Kohl\t0123456\r
3\ttitle2 tease\t\t\tfrei verfügbar\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tDossier\t2015\t1\tAnderer\tHelmut Schmidt, Helmut Kohl\t0123456\r
"""
        context = mock.Mock()
        context.year = 2015
        context.volume = 1
        toc = Toc(context, mock.Mock())
        res = toc._create_csv(self.toc_data)
        self.assertEqual(expected, res)

    def test_empty_page_node_in_xml_results_in_max_int_page_in_toc_entry(self):
        article = Article(StringIO(self.article_xml_template.format(page='')))
        self.repository['article'] = article
        article.updateDAVFromXML()
        t = Toc(mock.Mock(), mock.Mock())
        entry = t._create_toc_element(article)
        assert sys.maxsize == entry.get('page')

    def test_sorts_entries_with_max_int_page_as_last_toc_element(self):
        toc_data = {
            'Die Zeit': {
                'Politik': [
                    {'page': sys.maxsize, 'title': 'title2'},
                    {'page': 1, 'title': 'title1'},
                ]
            }
        }
        toc_data = OrderedDict(toc_data)
        t = Toc(mock.Mock(), mock.Mock())
        result = t._sort_toc_data(toc_data)
        assert sys.maxsize == result.get('Die Zeit').get('Politik')[-1].get('page')

    def test_excludes_given_property_values(self):
        for toc in [{'title': 'Heute 20.02.2016'}, {'supertitle': 'WIR RATEN AB'}]:
            self.assertFalse(Toc._is_relevant(toc))


class TocBrowserTest(zeit.content.volume.testing.BrowserTestCase):
    def setUp(self):
        super().setUp()
        # Create the volume object with the mock IConnector
        volume = Volume()
        volume.year = 2015
        volume.volume = 1
        volume.product = zeit.cms.content.sources.Product('ZEI')
        self.article_title = 'Ein Test Titel'
        self.ressort_names = ['dossier', 'politik']
        self.article_page = 1
        zeit.cms.content.add.find_or_create_folder('2015', '01')
        self.repository['2015']['01']['ausgabe'] = volume
        with zeit.cms.testing.interaction():
            for i, ressort in enumerate(self.ressort_names):
                article = create_article()
                article.ir_article_id = '012345%s' % i
                article.ir_mediasync_id = '98765%s' % i
                article.year = 2015
                article.volume = 1
                article.title = self.article_title
                article.subtitle = 'required'
                article.page = self.article_page
                article.printRessort = 'ressort %s' % ressort
                self.repository['2015']['01']['test_artikel_%s' % ressort] = article

    def test_toc_view_is_csv_file_download(self):
        b = self.browser
        with mock.patch(
            'zeit.content.volume.browser' '.toc.Toc._create_toc_content'
        ) as create_content:
            create_content.return_value = 'some csv'
            b.open('http://localhost/++skin++vivi/repository/' '2015/01/ausgabe/@@toc.csv')
            self.assertIn(b.headers['content-type'], ('text/csv', 'text/csv;charset=utf-8'))
            self.assertEqual(
                'attachment; ' 'filename="table_of_content_2015_01.csv"',
                b.headers['content-disposition'],
            )
            self.assertEllipsis('some csv', b.contents)

    def test_toc_generates_csv(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/' '2015/01/ausgabe/@@toc.csv')
        self.assertIn(self.article_title, b.contents)
        self.assertIn(str(self.article_page), b.contents)
        for ressort_name in self.ressort_names:
            self.assertIn('ressort %s' % ressort_name, b.contents)
        self.assertIn('DIE ZEIT'.lower(), b.contents.lower())
