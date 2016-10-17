# -*- coding: utf-8 -*-
import StringIO

import zeit.cms.browser.view
import csv
import tinydav
import logging
log = logging.getLogger(__name__)

# Does the DAV Content need to be locked while reading? I guess not

"""
a = davclient.propfind("cms/archiv-wf/archiv/ZECH/2009/51/politik/")
a._etree"""

class Toc(zeit.cms.browser.view.Base):
    """
    View for creating a Table of Content as a csv file.
    """
    # TODO use volume-field instead of passing the obj in almost every method
    # Get this form a config File
    DAV_SERVER_ROOT = "cms-backend.zeit.de/cms/archiv-wf/archiv/"
    PORT = 9000
    # The Volume Content Object will get extended so
    # this hardcoded stuff shouldn't be necassary
    PRINT_PRODUCT_ID = 'ZEI'
    # 'CW' in Ticket Description, changed it to 'ZWCW'
    REGIONAL_PRODUCT_IDS = ['ZESA', 'ZEIH', 'ZEOE', 'ZECH', 'ZECW']
    CSV_DELIMITER = ''

    def __call__(self):
        self.volume = self.context
        volume = self.context
        filename = self._generate_file_name(volume)
        self.request.response.setHeader('Content-Type', 'text/csv')
        self.request.response.setHeader('Content-Disposition', 'attachment; filename="%s"' % filename)
        return self._create_toc_content(volume)

    def _create_toc_content(self, volume):
        """
        Create Table of Contents for the given Volume as a csv.
        :param volume: ..volume.Volume Content Instance
        :return: Specify
        """
        toc_data = self._get_via_dav()
        return self._create_csv(toc_data)

    def _generate_file_name(self, volume):
        # Internationalization?
        return "inhalsverzeichnis_{}_{}.csv".format(volume.year, volume.volume)

    def _get_via_dav(self):
        """
        Get and parse xml form webdav und create toc entries.
        :param volume: ..volume.Volume Content Instance
        :return: Sorted List of Toc entries
                 [{'ressort': str, 'page': int, 'title': str, "teaser": str}]
        """
        results = []
        product_ids = self._get_all_product_ids_for_volume()
        product_id_paths = self._get_all_paths_for_prodct_ids(product_ids)
        client = self._create_dav_client()
        for path in product_id_paths:
            for doc_path in self._get_all_docs_in_path(path):
                tree = self._parse_xml(client, doc_path)
                if self._is_relevant_doc(tree):
                    results.append(self._get_metadata_from_from_xml_content(tree))
        return results

    def _get_all_product_ids_for_volume(self):
        """ Returns sorted List [First Product in TOC, Second ...] """
        # Change this if the volume content object "knows" which Products it has...
        return [self.PRINT_PRODUCT_ID] + self.REGIONAL_PRODUCT_IDS

    def _get_all_paths_for_prodct_ids(self, product_ids):
        # http://cms-backend.zeit.de:9000/cms/archiv-wf/archiv/ZECH/2009/51/politik/CH-Fetz
        return ["{}/{}/{}".format(product_id, self.volume.year, self.volume.volume)
                for product_id in product_ids]

    def _is_relevant_doc(self, tree):
        """
        Predicate to decide if a doc is relevant for the toc.
        :param tree: lxml.etree of the doc
        :return: bool
        """
        # TODO
        return True

    def _create_dav_client(self):
        # TODO Get uri from some config
        return tinydav.WebDAVClient(self.DAV_SERVER_ROOT, self.PORT)

    def _get_metadata_from_xml_content(self, etree):
        # TODO is the subtitle the teaser?
        # TODO Xpath text() might return a list!
        xpaths = {
            'title': "article/body/title/text()",
            'page': "//attribute[@name='page']/text()",
            'teaser': "article/body/subtitle/text()",
            'ressort': "//attribute[@name='ressort and @ns='http://namespaces.zeit.de/CMS/document']/text()"
        }
        res = {}
        for key, xpath in xpaths:
            res[key] = etree.xpath(xpath)
        return res

    def _create_csv(self, toc_data):
        """
        Creates CSV File from TOC Data.
        RESSORT [tab] SEITENZAHL [tab] TITEL + TEASER
        :param toc_data:
        :return: The CSV-File.
        """

        try:
            delimiter = '\t'
            file_content = u''
            out = StringIO.StringIO()
            writer = csv.writer(out, delimiter=delimiter)
            for toc_element in self._format_toc_elements(toc_data):
                writer.write_row(toc_element)
            file_content = out.getvalue()
        finally:
            out.close()
            return file_content

    def _format_toc_elements(self, toc_entries):
        for toc_entry in toc_entries:
            yield self._format_toc_element(toc_entry)
        return

    def _format_toc_element(self, toc_entry):
        # TODO Other fields need to be normalized too, e.g. page
        tit_and_tease = toc_entry.get("title") + " " + toc_entry.get("title")
        return [toc_entry.get("ressort"), toc_entry.get("page"), tit_and_tease]
