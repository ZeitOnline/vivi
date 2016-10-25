#!/usr/bin/env python
# -*- coding: utf-8 -*-
import mock
import zeit.cms.testing
from zeit.cms.repository.folder import Folder
from zeit.content.article.testing import create_article
from zeit.content.volume.browser.toc import Toc
from zeit.content.volume.volume import Volume
import zeit.cms.content.sources
import zeit.content.volume.testing
import lxml.etree
import posixpath


class TocFunctionalTest(zeit.content.volume.testing.FunctionalTestCase):

    def setUp(self):
        super(TocFunctionalTest, self).setUp()

    def test_parse_article_returns_an_lxml_object(self):
        xml = """<xml/>"""
        doc_path = '/cms/archiv-wf/archiv/ZEI/2009/23/test_article'
        toc = Toc()
        with mock.patch("tinydav.WebDAVClient.get") as get:
            response = mock.Mock()
            response.content = xml
            get.return_value = response
            result = toc._parse_article(doc_path)
        self.assertEqual(xml, lxml.etree.tostring(result))

    def test_list_relevant_dirs_with_dav_returns_no_images_or_leserbriefe_directories(self):
        dir_path = '/cms/archiv-wf/archiv/ZEI/2009/23/'
        toc = Toc()
        with mock.patch('tinydav.WebDAVClient.propfind') as propfind:
            response = mock.MagicMock()
            response.is_multistatus = True
            hrefs = ['images', 'leserbriefe', 'politik']
            image_element = mock.Mock()
            leserbriefe_element = mock.Mock()
            politik_element = mock.Mock()
            # Make the response iterable like tinydav Response
            elements = [image_element, leserbriefe_element, politik_element]
            for ele, href in zip(elements, hrefs):
                ele.href = posixpath.join(dir_path, href)
                get_mock = mock.Mock()
                get_mock.text = 'unix-directory'
                ele.get.return_value = get_mock
            response.__iter__ = mock.Mock(return_value=iter([image_element, leserbriefe_element, politik_element]))
            propfind.return_value = response
            result = toc.list_relevant_dirs_with_dav(dir_path)
            self.assertEqual(result, [elements[2].href])




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

    def test_toc_menu_generate_csv(self):
        b = self.browser
        b.handleErrors = False
        b.open('http://localhost/++skin++vivi/repository/'
               'ZEI/2015/01/ausgabe/@@toc.csv')
        self.assertEllipsis("some csv", b.contents)

# TocFunctionalTest().test_list_relevant_dirs_with_dav_returns_no_images_or_leserbriefe_directories()
