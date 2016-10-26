#!/usr/bin/env python
# -*- coding: utf-8 -*-
import mock
import zeit.cms.testing
from ordereddict import OrderedDict
from zeit.cms.repository.folder import Folder
from zeit.content.article.testing import create_article
from zeit.content.volume.browser.toc import Toc
from zeit.content.volume.volume import Volume
import zeit.cms.content.sources
import zeit.content.volume.testing
import posixpath

# TODO Get via DAV Test
# TODO sort Toc Test

class TocFunctionalTest(zeit.content.volume.testing.FunctionalTestCase):

    def setUp(self):
        super(TocFunctionalTest, self).setUp()


    def test_list_relevant_dirs_with_dav_returns_correct_directories(self):
        dir_path = '/cms/archiv-wf/archiv/ZEI/2009/23/'
        toc = Toc()
        with mock.patch('tinydav.WebDAVClient.propfind') as propfind:
            response = mock.MagicMock()
            response.is_multistatus = True
            hrefs = ['images', 'leserbriefe', 'politik']
            image_element = mock.Mock()
            leserbriefe_element = mock.Mock()
            politik_element = mock.Mock()
            # Mock the dir_path status for tinydav
            dir_path_element = mock.Mock()
            dir_path_element.href = dir_path
            dir_get_mock = mock.Mock()
            dir_get_mock.text = 'unix-directory'
            dir_path_element.get.return_value = dir_get_mock
            elements = [image_element, leserbriefe_element, politik_element]
            for ele, href in zip(elements, hrefs):
                ele.href = posixpath.join(dir_path, href)
                get_mock = mock.Mock()
                get_mock.text = 'unix-directory'
                ele.get.return_value = get_mock
            # Make the response iterable like tinydav Response
            response.__iter__ = mock.Mock(return_value=iter([image_element, leserbriefe_element, politik_element,
                                                             dir_path_element]))
            propfind.return_value = response
            result = toc.list_relevant_dirs_with_dav(dir_path)
            self.assertEqual(result, [elements[2].href])

    def test_create_toc_element_from_xml_with_linebreak_in_teaser(self):
        xml = u"""
        <article>
            <head>
                <attribute ns="http://namespaces.zeit.de/CMS/document" name="page">20-20</attribute>
                <attribute ns="http://namespaces.zeit.de/CMS/document" name="author">Autor</attribute>
            </head>
            <body>
                 <title>Titel</title>
                 <subtitle>Das soll der Teaser
                 sein</subtitle>
            </body>
        </article>
        """
        expected = {'page': '20', 'title': 'Titel', 'teaser': 'Das soll der Teaser sein', 'author': 'Autor'}
        doc_path = '/cms/archiv-wf/archiv/ZEI/2009/23/test_article'
        toc = Toc()
        with mock.patch("tinydav.WebDAVClient.get") as get:
            response = mock.Mock()
            response.content = xml
            get.return_value = response
            result = toc._create_toc_element(doc_path)
        self.assertEqual(expected, result)

    def test_create_csv_with_all_values_in_toc(self):
        # TODO Refactor
        toc_data = OrderedDict()
        toc_data['Die Zeit'] = OrderedDict(
                    {'Politik': [{'page': '1', 'title': 'title', 'teaser':'tease', 'author':'Autor'}]})
        toc_data['Anderer'] = OrderedDict(
                    {'Dossier': [{'page': '1', 'title': 'title', 'teaser':'tease', 'author':'Autor'},
                                 {'page': '3', 'title': 'title2', 'teaser':'tease', 'author':'Autor'}
                                 ]}
                )
        expected = """Die Zeit\r
Politik\r
1\tAutor\ttitle tease\r
Anderer\r
Dossier\r
1\tAutor\ttitle tease\r
3\tAutor\ttitle2 tease\r
"""
        toc= Toc()
        res = toc._create_csv(toc_data)
        self.assertEqual(expected, res)


class TocBrowserTest(zeit.cms.testing.BrowserTestCase):
    layer = zeit.content.volume.testing.ZCML_LAYER

    def setUp(self):
        super(TocBrowserTest, self).setUp()
        volume = Volume()
        volume.year = 2015
        volume.volume = 1
        volume.product = zeit.cms.content.sources.Product(u'ZEI')
        # Browser needs this model stuff
        with zeit.cms.testing.site(self.getRootFolder()):
            self.repository['ZEI'] = Folder()
            self.repository['ZEI']['2015'] = Folder()
            self.repository['ZEI']['2015']['01'] = Folder()
            self.repository['ZEI']['2015']['01']['ausgabe'] = volume
            self.repository['ZEI']['2015']['01']['dossier'] = Folder()
            self.repository['ZEI']['2015']['01']['politik'] = Folder()
            with zeit.cms.testing.interaction():
                article = create_article()
                article.year = 2015
                article.volume = 1
                article.title = "Ein Test Titel"
                article.page = 1
                self.repository['ZEI']['2015']['01']['politik']['test_artikel'] = article


    # TODO Dav-client umbiegen?
    def test_toc_menu_generate_csv(self):
        b = self.browser
        b.handleErrors = False
        b.open('http://localhost/++skin++vivi/repository/'
               'ZEI/2015/01/ausgabe/@@toc.csv')
        self.assertEllipsis("some csv", b.contents)

