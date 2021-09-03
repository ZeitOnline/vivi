# -*- coding: utf-8 -*-
from collections import defaultdict, OrderedDict
from unittest import mock
from zeit.cms.repository.folder import Folder
from zeit.content.article.testing import create_article
from zeit.content.volume.browser.toc import Toc, Excluder
from zeit.content.volume.volume import Volume
import lxml.etree
import sys
import zeit.cms.content.add
import zeit.cms.content.sources
import zeit.cms.testing
import zeit.content.volume.interfaces
import zeit.content.volume.testing
import zope.component


class TocFunctionalTest(zeit.content.volume.testing.FunctionalTestCase):

    def setUp(self):
        super(TocFunctionalTest, self).setUp()
        self.toc_data = OrderedDict()
        self.toc_data['Die Zeit'] = OrderedDict(
            {'Politik': [{'page': '1',
                          'title': 'title',
                          'teaser': 'tease',
                          'access': u'frei verfügbar',
                          'volume': u'1',
                          'year': u'2015',
                          'supertitle': 'Super'}]
             }
        )
        self.toc_data['Anderer'] = OrderedDict(
            {'Dossier': [
                {'page': '1',
                 'access': u'frei verfügbar',
                 'title': 'title',
                 'teaser': 'tease',
                 'supertitle': 'Super',
                 'volume': '1',
                 'year': '2015',
                 },
                {'page': '3',
                 'access': u'frei verfügbar',
                 'title': 'title2',
                 'teaser': 'tease',
                 'volume': '1',
                 'year': '2015',
                 'supertitle': 'Super'}
            ]}
        )
        self.article_xml_template = u"""
            <article>
                <head>
                    <attribute ns="http://namespaces.zeit.de/CMS/document"
                    name="page">{page}</attribute>
                    <attribute ns="http://namespaces.zeit.de/CMS/document"
                    name="access">free</attribute>
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
        toc = Toc(mock.Mock(), mock.Mock())
        toc_connector = zope.component.getUtility(
            zeit.content.volume.interfaces.ITocConnector)
        zope.component.getGlobalSiteManager().registerUtility(
            toc_connector, zeit.connector.interfaces.IConnector)
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

    def test_create_toc_element_should_flatten_linebreaks(self):
        article_xml = self.article_xml_template.format(page='20-20')
        expected = {'page': 20,
                    'title': 'Titel',
                    'teaser': 'Das soll der Teaser sein',
                    'supertitle': '',
                    'access': u'frei verfügbar'
                    }
        article_element = lxml.etree.fromstring(article_xml)
        toc = Toc(mock.Mock(), mock.Mock())
        result = toc._create_toc_element(article_element)
        self.assertEqual(expected, result)

    def test_csv_is_created_from_toc_data(self):
        expected = """1\ttitle tease\t\t\tfrei verfügbar\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tPolitik\t2015\t1\tDie Zeit\r
1\ttitle tease\t\t\tfrei verfügbar\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tDossier\t2015\t1\tAnderer\r
3\ttitle2 tease\t\t\tfrei verfügbar\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tDossier\t2015\t1\tAnderer\r
"""
        context = mock.Mock()
        context.year = 2015
        context.volume = 1
        toc = Toc(context, mock.Mock())
        res = toc._create_csv(self.toc_data)
        self.assertEqual(expected, res)

    def test_empty_page_node_in_xml_results_in_max_int_page_in_toc_entry(self):
        article_xml = self.article_xml_template.format(page='')
        article_element = lxml.etree.fromstring(article_xml)
        t = Toc(mock.Mock(), mock.Mock())
        entry = t._create_toc_element(article_element)
        assert sys.maxsize == entry.get('page')

    def test_sorts_entries_with_max_int_page_as_last_toc_element(self):
        toc_data = {
            'Die Zeit': {
                'Politik':
                    [
                        {'page': sys.maxsize, 'title': 'title2'},
                        {'page': 1, 'title': 'title1'}
                    ]
            }
        }
        toc_data = OrderedDict(toc_data)
        t = Toc(mock.Mock(), mock.Mock())
        result = t._sort_toc_data(toc_data)
        assert sys.maxsize == result.get('Die Zeit').get('Politik')[-1].get(
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

    def test_toc_connector_is_registered_as_connector(self):
        old_connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        # register_archive_connector is called in __init__
        # check for the correct side effects
        t = Toc(mock.Mock(), mock.Mock())
        with t._register_archive_connector():
            new_connector = zope.component.getUtility(
                zeit.connector.interfaces.IConnector)
            # Check if a new IConnector was registered
            assert old_connector is not new_connector
            # Check if the toc.connector is the ITocConnector
            assert t.connector is zope.component.getUtility(
                zeit.content.volume.interfaces.ITocConnector)
            assert t.connector is zope.component.getUtility(
                zeit.connector.interfaces.IConnector)


class TocBrowserTest(zeit.content.volume.testing.BrowserTestCase):

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
        zeit.cms.content.add.find_or_create_folder('2015', '01')
        self.repository['2015']['01']['ausgabe'] = volume
        # Now use the mock ITocConnector to mock the archive folders and the
        # article
        toc_connector = zope.component.getUtility(
            zeit.content.volume.interfaces.ITocConnector)
        sm = zope.component.getSiteManager()
        sm.registerUtility(toc_connector, zeit.connector.interfaces.IConnector)
        with zeit.cms.testing.site(self.getRootFolder()):
            for ressort_name in self.ressort_names:
                zeit.cms.content.add.find_or_create_folder(
                    'ZEI', '2015', '01', ressort_name)
            with zeit.cms.testing.interaction():
                article = create_article()
                article.year = 2015
                article.volume = 1
                article.title = self.article_title
                article.page = self.article_page
                self.repository['ZEI']['2015']['01']['politik'][
                    'test_artikel'] = article
                article = create_article()
                article.year = 2015
                article.volume = 1
                article.title = self.article_title
                article.page = self.article_page
                self.repository['ZEI']['2015']['01']['dossier'][
                    'test_artikel_dossier'] = article
        sm.registerUtility(
            zope.component.getGlobalSiteManager().getUtility(
                zeit.connector.interfaces.IConnector),
            zeit.connector.interfaces.IConnector)

    def test_toc_view_is_csv_file_download(self):
        b = self.browser
        with mock.patch('zeit.content.volume.browser'
                        '.toc.Toc._create_toc_content') as create_content:
            create_content.return_value = 'some csv'
            b.open('http://localhost/++skin++vivi/repository/'
                   '2015/01/ausgabe/@@toc.csv')
            self.assertIn(b.headers['content-type'],
                          ('text/csv', 'text/csv;charset=utf-8'))
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
