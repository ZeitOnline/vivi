#!/usr/bin/env python
# -*- coding: utf-8 -*-
import mock
from ordereddict import OrderedDict
import posixpath
import zeit.cms.testing
from zeit.cms.repository.folder import Folder
from zeit.content.article.testing import create_article
from zeit.content.volume.browser.toc import Toc
from zeit.content.volume.volume import Volume
import zeit.cms.content.sources
import zeit.content.volume.testing

article_xml = u"""
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

def create_tinydav_propfind_mock_response(directory_or_file_names, path, dir=False):
    """
    Helper to create a tinydav response mock object, for a propfind
    call.
    :param directory_or_file_names: [str] - hrefs of status objects to be created
    :param path: str - path of the propfind tinydav call
    :param dir: bool - specifies if propfind is expected to find directories
    :return: mock.Mock - tinydav response Mock object
    """
    response = mock.Mock()
    response.is_multistatus = True
    dir_path_element = mock.Mock()
    dir_path_element.href = path
    dir_get_mock = mock.Mock()
    dir_get_mock.text = 'unix-directory'
    dir_path_element.get.return_value = dir_get_mock
    status_elements = [dir_path_element]
    for href in directory_or_file_names:
        ele = mock.Mock()
        ele.href = posixpath.join(path, href, '')
        get_mock = mock.Mock()
        if dir:
            get_mock.text = 'unix-directory'
        else:
            # This is dirty. It only prevents:
            # return 'directory' in status_element.get('getcontenttype').text
            # TypeError: argument of type 'Mock' is not iterable
            get_mock.text = ''
        ele.get.return_value = get_mock
        status_elements.append(ele)
    response.__iter__ = mock.Mock(return_value=iter(status_elements))
    return response


class TocFunctionalTest(zeit.content.volume.testing.FunctionalTestCase):

    def setUp(self):
        super(TocFunctionalTest, self).setUp()
        self.toc_data = OrderedDict()
        self.toc_data['Die Zeit'] = OrderedDict(
                    {'Politik': [{'page': '1', 'title': 'title', 'teaser':'tease', 'author': 'Autor'}]})
        self.toc_data['Anderer'] = OrderedDict(
                    {'Dossier': [{'page': '1', 'title': 'title', 'teaser':'tease', 'author': 'Autor'},
                                 {'page': '3', 'title': 'title2', 'teaser':'tease', 'author': 'Autor'}
                                 ]}
                )

    def test_list_relevant_dirs_with_dav_returns_correct_directories(self):
        dir_path = '/cms/archiv-wf/archiv/ZEI/2009/23/'
        toc = Toc()
        with mock.patch('tinydav.WebDAVClient.propfind') as propfind:
            hrefs = ['images', 'leserbriefe', 'politik']
            propfind.return_value = create_tinydav_propfind_mock_response(hrefs, dir_path, True)
            result = toc.list_relevant_dirs_with_dav(dir_path)
            self.assertEqual(1, len(result))
            assert 'politik' in result[0]

    def test_create_toc_element_from_xml_with_linebreak_in_teaser(self):
        expected = {'page': '20', 'title': 'Titel', 'teaser': 'Das soll der Teaser sein', 'author': 'Autor'}
        doc_path = '/cms/archiv-wf/archiv/ZEI/2009/23/test_article'
        toc = Toc()
        with mock.patch("tinydav.WebDAVClient.get") as get:
            response = mock.Mock()
            response.content = article_xml
            get.return_value = response
            result = toc._create_toc_element(doc_path)
        self.assertEqual(expected, result)

    def test_create_csv_with_all_values_in_toc_data(self):
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

    def test_create_csv_with_not_all_values_in_toc_data(self):
        # Delete an author in input toc data
        product, ressort_dict = self.toc_data.iteritems().next()
        ressort, article_list = ressort_dict.iteritems().next()
        article_list[0]['author'] = ''
        input_data = {product: {ressort: article_list}}
        toc = Toc()
        assert toc.CSV_DELIMITER*2 in toc._create_csv(input_data)


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

    def test_toc_generates_right_headers(self):
        b = self.browser
        b.handleErrors = False
        # TODO language header for vivi?
        # b.addHeader('Accept-Language', 'de')
        # b.addHeader('Content-Language', 'de')
        with mock.patch('zeit.content.volume.browser.toc.Toc._create_toc_content') as create_content:
            create_content.return_value = 'some csv'
            b.open('http://localhost/++skin++vivi/repository/'
                   'ZEI/2015/01/ausgabe/@@toc.csv')
            self.assertEqual('text/csv', b.headers['content-type'])
            self.assertEqual('attachment; filename="table_of_content_2015_1.csv"', b.headers['content-disposition'])
            self.assertEllipsis("some csv", b.contents)



    @mock.patch('tinydav.WebDAVClient.get')
    @mock.patch('tinydav.WebDAVClient.propfind')
    @mock.patch('zeit.content.volume.browser.toc.Toc._get_all_product_ids_for_volume', return_value=['ZEI'])
    def test_toc_generates_correct_csv(self, mock_products, mock_propfind, mock_get):
        ressort_name = 'poltik'

        def propfind_helper(path, **kwargs):
            if path.endswith('/01/'):
                return create_tinydav_propfind_mock_response([ressort_name], path, dir=True)
            elif path.endswith('/01/{}/'.format(ressort_name)):
                return create_tinydav_propfind_mock_response(['article'], path, dir=False)
            else:
                pass

        mock_propfind.side_effect = propfind_helper
        get_response = mock.Mock()
        get_response.content = article_xml
        mock_get.return_value = get_response
        b = self.browser
        csv = "20{delim}Autor{delim}Titel Das soll der Teaser sein".format(delim=Toc.CSV_DELIMITER)
        b.handleErrors = False
        b.open('http://localhost/++skin++vivi/repository/'
               'ZEI/2015/01/ausgabe/@@toc.csv')
        self.assertEqual(2, mock_propfind.call_count)
        self.assertIn(csv, b.contents)
        self.assertIn(ressort_name.title(), b.contents)
