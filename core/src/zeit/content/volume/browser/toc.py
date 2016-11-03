# -*- coding: utf-8 -*-
import StringIO
import csv
import tinydav
import re
import sys
import lxml.etree
import posixpath
from ordereddict import OrderedDict
import zeit.cms.browser.view
from tinydav.exception import HTTPUserError
from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.sources

# TODO Right now every article is relevant, Production will provide a list of articles/list in toc_config.py
# TODO Author/Text contains Tabs Bug Fix neccessary 2016/23
from zeit.content.volume.browser.toc_config import ArticleExcluder


class Toc(zeit.cms.browser.view.Base):
    """
    View for creating a Table of Content as a csv file.
    """
    # Get this form a config File?
    DAV_SERVER_ROOT = "cms-backend.zeit.de"
    DAV_PORT = 9000
    DAV_ARCHIVE_ROOT = "/cms/archiv-wf/archiv"
    # Not all directories in the archives are named the product ID.
    PRODUCT_ID_DIR_NAME_EXCEPTIONS = {'CW': 'ZECW'}
    # this hardcoded stuff shouldn't be necassary
    # The Volume Content Object will get extended soon
    # The Order of the Product ID's matters, First in this list -> first in TOC
    PRODUCT_IDS = ['ZEI', 'ZESA', 'ZEIH', 'ZEOE', 'ZECH', 'CW']
    CSV_DELIMITER = '\t'

    def __init__(self, *args, **kwargs):
        super(Toc, self).__init__(*args, **kwargs)
        self.client = self._create_dav_client()
        self.article_excluder = ArticleExcluder()

    def __call__(self):
        self.volume = self.context
        self.product_id_mapping = self._create_product_id_full_name_mapping()
        filename = self._generate_file_name()
        self.request.response.setHeader('Content-Type', 'text/csv')
        self.request.response.setHeader('Content-Disposition', 'attachment; filename="%s"' % filename)
        return self._create_toc_content()

    def _create_toc_content(self):
        """
        Create Table of Contents for the given Volume as a csv.
        :param volume: ..volume.Volume Content Instance
        :return: Specify
        """
        toc_data = self._get_via_dav()
        sorted_toc_data = self._sort_toc_data(toc_data)
        return self._create_csv(sorted_toc_data)

    def _generate_file_name(self):
        toc_file_string = _("Table of Content").lower().replace(" ", "_")
        return "{}_{}_{}.csv".format(toc_file_string, self.volume.year, self.volume.volume)

    def _get_via_dav(self):
        """
        Get and parse xml form webdav und create toc entries.
        :param volume: ..volume.Volume Content Instance
        :return: Sorted List of Toc entries
                 [{'ressort': str, 'page': str, 'title': str, "teaser": str}]
        """
        """
            {
                "Die Zeit: {
                        {"Politk: [sorted_toc_entrires]"}
                    }
            }
            sorted_toc_entries: [{'page': str, 'title': str, "teaser": str}, ...]
        """
        results = OrderedDict()
        product_ids = self._get_all_product_ids_for_volume()
        for product_path in self._get_all_paths_for_prodct_ids(product_ids):
            result_for_product = {}
            for ressort_path in self.list_relevant_ressort_dirs_with_dav(product_path):
                result_for_ressort = []
                for article_path in self._get_all_articles_in_path(ressort_path):
                    toc_entry = self._create_toc_element(article_path)
                    if toc_entry:
                        result_for_ressort.append(toc_entry)
                result_for_product[self._dir_name(ressort_path)] = result_for_ressort
            results[self._full_product_name(product_path)] = result_for_product
        return results

    def _get_all_articles_in_path(self, path):
        """ Expects like cms/archiv-wf/archiv/ZESA/2015/02/ """
        all_articles = []
        for article_path in self._get_all_files_in_folder(path):
            all_articles.append(article_path)
        return all_articles

    def _parse_article(self, doc_path):
        """
        Parse the artice XML.
        :param doc_path: path to artice xml on DAV-Server.
        """
        try:
            response = self.client.get(doc_path)
            return lxml.etree.fromstring(response.content)
        except:
            raise

    def _get_all_product_ids_for_volume(self):
        """ Returns sorted List [First Product in TOC, Second ...] """
        # Change this if the volume content object "knows" which Products it has...
        return self.PRODUCT_IDS

    def _get_all_paths_for_prodct_ids(self, product_ids):
        """
        Creates a list of unix-paths to all given products
        :param product_ids: [str]
        :return: [str]
        """
        product_dir_names = [self._replace_product_id_by_its_dirname(product_id) for product_id in product_ids]
        volume_string = str(self.volume.volume)
        # Volumes <10 would lead to wrong paths like YEAR/1 instead of YEAR/01
        if self.volume.volume < 10:
            volume_string = '0' + volume_string
        return [posixpath.join(*[str(e) for e in [self.DAV_ARCHIVE_ROOT, dir_name, self.volume.year, volume_string, '']])
                for dir_name in product_dir_names]

    def _replace_product_id_by_its_dirname(self, product_id, reverse=False):
        """
        :param product_id: str
        :param reverse: Bool - replace directorynames with product ID's instead.
        :return: str
        """
        if reverse:
            new_dict = {}
            for k, v in self.PRODUCT_ID_DIR_NAME_EXCEPTIONS.iteritems():
                new_dict[v] = k
            result = new_dict.get(product_id, product_id)
        else:
            result = self.PRODUCT_ID_DIR_NAME_EXCEPTIONS.get(product_id, product_id)
        return result

    def _is_relevant_article(self, article_tree):
        """
        Predicate to decide if a doc is relevant for the toc.
        :param article_tree: lxml.etree  of the article
        :return: bool
        """
        return self.article_excluder.is_relevant(article_tree)

    def _create_dav_client(self):
        # TODO Get uri from some config (zope.conf)?
        return tinydav.WebDAVClient(self.DAV_SERVER_ROOT, self.DAV_PORT)

    def _get_metadata_from_article_xml(self, tree):
        xpaths = {
            'title': "body/title/text()",
            'page': "//attribute[@name='page']/text()",
            'teaser': "body/subtitle/text()",
            'author': "//attribute[@name='author']/text()"
        }
        res = {}
        for key, xpath in xpaths.iteritems():
            res[key] = tree.xpath(xpath)
        return self._normalize_toc_element(res)

    def list_relevant_ressort_dirs_with_dav(self, path):
        """ Returns all relevant ressort paths to directories for a given path """
        try:
            response = self.client.propfind(path, depth=1)
            assert response.is_multistatus
            return [element.href for element in response if self._is_relevant_path_to_directory(path, element)]
        except HTTPUserError:
            return []

    def _is_relevant_path_to_directory(self, root_path_of_element, element):
        try:
            # TODO Put this in the excluder
            folders_to_exclude = {'images', 'leserbriefe'}
            folders_to_exclude = set.union(folders_to_exclude, {ele.title() for ele in folders_to_exclude})
            root_paths = {root_path_of_element, '/' + root_path_of_element}
            return self._is_dav_dir(element) \
                   and not any(folder in element.href for folder in folders_to_exclude) \
                   and element.href not in root_paths
        except:
            raise

    def _get_all_files_in_folder(self, ressort_path):
        response = self.client.propfind(ressort_path, depth=1)
        assert response.is_multistatus
        return [status_element.href for status_element in response if not self._is_dav_dir(status_element)]

    def _is_dav_dir(self, status_element):
        try:
            return 'directory' in status_element.get('getcontenttype').text
        except AttributeError:
            return False

    def _create_csv(self, toc_data):
        """
        Creates CSV File from TOC Data.
        SEITENZAHL [tab] TITEL + TEASER
        :param toc_data:
        :return: The CSV-File.
        """

        file_content = u''
        out = StringIO.StringIO()
        try:
            writer = csv.writer(out, delimiter=self.CSV_DELIMITER)
            for toc_element in self._generate_csv_rows(toc_data):

                writer.writerow(
                    [val.encode('utf-8') for val in toc_element]
                )

            file_content = out.getvalue()
        finally:
            out.close()
            return file_content

    def _generate_csv_rows(self, toc_entries):
        """
        Generator to create the csv-rows.
        :param toc_entries: TODO
        :return: [CSV Row]
        """
        for product_name, ressort_dict in toc_entries.iteritems():
            yield [product_name]
            for ressort_name, toc_entries in ressort_dict.iteritems():
                yield [ressort_name]
                for toc_entry in toc_entries:
                    yield self._format_toc_element(toc_entry)
        return

    def _format_toc_element(self, toc_entry):
        title_and_tease = toc_entry.get("title") + u" " + toc_entry.get("teaser")
        return [toc_entry.get("page"), toc_entry.get("author"), title_and_tease]

    def _normalize_toc_element(self, toc_entry):
        for key, value in toc_entry.iteritems():
            toc_entry[key] = value[0].replace(self.CSV_DELIMITER, '') if len(value) > 0 else u""
        self._normalize_teaser(toc_entry)
        self._normalize_page(toc_entry)
        return toc_entry

    def _normalize_page(self, toc_dict):
        page_string = toc_dict.get('page', u'')
        res = re.findall('\d+', page_string)
        toc_dict['page'] = res[0].lstrip("0") if res else u"-1"

    def _normalize_teaser(self, toc_entry):
        """Delete linebreaks and a too much whitespace"""
        teaser = toc_entry.get('teaser', u'')
        toc_entry['teaser'] = teaser.replace('\n', u' ')
        toc_entry['teaser'] = re.sub(r'\s\s+', u' ', teaser)

    def _create_toc_element(self, doc_path):
        article_element = self._parse_article(doc_path)
        return self._get_metadata_from_article_xml(article_element) \
            if self._is_relevant_article(article_element) else None

    def _dir_name(self, path):
        return path.split('/')[-2].title()

    def _create_product_id_full_name_mapping(self):
        products = list(zeit.cms.content.sources.PRODUCT_SOURCE(self.context))
        return dict([(product.id, product.title) for product in products])

    def _full_product_name(self, product_path):
        """
        :param product_path: str -  /PRODUCT_ID/YEAR/VOL/
        """
        splitted_path = product_path.split(posixpath.sep)
        product_id = splitted_path[-4]
        return self.product_id_mapping.get(product_id, product_id)

    def _sort_toc_data(self, toc_data):
        """
        :param toc_data:
        :return:
        """
        # TODO Think about a better way to sort the toc!
        for product_name, ressort_dict in toc_data.iteritems():
            for ressort_name, articles in ressort_dict.iteritems():
                toc_data[product_name][ressort_name] = self._sorted_articles(articles)
        for product_name, ressort_dict in toc_data.iteritems():
            toc_data[product_name] = self._sorted_ressorts(ressort_dict)
        return toc_data

    def _get_page_from_article(self, article):
        """
        :param article: {'page':str}
        :return: int
        """
        try:
            return int(article.get('page'))
        except ValueError:
            # The empty string will cause a Value Error
            return sys.maxint

    def _sorted_articles(self, articles):
        return sorted(articles, key=self._get_page_from_article)

    def _sorted_ressorts(self, ressorts):
        # Expects articles in ressorts dict to be sorted by page
        ressort_min_page_number_tuples = []
        for resort_name, articles in ressorts.iteritems():
            # Empty ressorts should be listed as last entries in toc
            min_page = sys.maxint
            if articles:
                min_page = self._get_page_from_article(articles[0])
            ressort_min_page_number_tuples.append((resort_name, min_page))
        d = OrderedDict()
        for ressort_min_page_tuple in sorted(ressort_min_page_number_tuples, key=lambda resort_page_tup: resort_page_tup[1]):
            d[ressort_min_page_tuple[0]] = ressorts.get(ressort_min_page_tuple[0])
        return d
