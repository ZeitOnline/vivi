# -*- coding: utf-8 -*-
import StringIO
import zeit.connector.dav.davresource
import zeit.cms.browser.view
import csv
import tinydav
import logging
import re
log = logging.getLogger(__name__)

# Does the DAV Content need to be locked while reading? I guess not
# TODO Exclude Inhaltsverzeichnis maybe even ressort Verschiedenes
# TODO Product-ID's via ./work/source/zeit.cms/src/zeit/cms/content/products.xml ?

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

    def _get_metadata_from_xml_content(self, tree):
        # TODO Xpath text() might return a list!
        xpaths = {
            'title': "body/title/text()",
            'page': "//attribute[@name='page']/text()",
            'teaser': "body/subtitle/text()",
            'ressort': "//attribute[@name='ressort' and @ns='http://namespaces.zeit.de/CMS/document']/text()"
        }
        res = {}
        for key, xpath in xpaths.iteritems():
            res[key] = tree.xpath(xpath)
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
        self._normalize_toc_element(toc_entry)
        tit_and_tease = toc_entry.get("title") + u" " + toc_entry.get("teaser")
        return [toc_entry.get("ressort"), toc_entry.get("page"), tit_and_tease]


    def list_dir(self, client, path):
        """ Returns all paths to directories for a given path """
        response = client.propfind(path, depth=1)
        # How to deal with this error
        assert response.is_multistatus
        return [element.href for element in response if self._is_path_to_directory(path, element)]

    def _is_path_to_directory(self, root_path_of_element, element):
        # Dont include the root_path_of_elemnt itself
        root_paths = {root_path_of_element, '/' + root_path_of_element}
        return 'directory' in element.get('getcontenttype').text and element.href not in root_paths

    def _normalize_toc_element(self, toc_entry):
        for key, value in toc_entry.iteritems():
            toc_entry[key] = value[0] if len(value) > 0 else "Nicht ermittelt"
        self._normalize_teaser(toc_entry)
        self._normalize_page(toc_entry)

    def _normalize_page(self, toc_dict):
        page_string =toc_dict.get('page', '')
        res = re.findall('\d+', page_string)
        toc_dict['page']= res[0].strip("0") if res else "Nicht ermittelt"

    def _normalize_teaser(self, toc_entry):
        teaser = toc_entry.get('teaser','')
        # Delete Linebreaks and a whitespace
        toc_entry['teaser'] = teaser.replace('\n','')
        toc_entry['teaser'] = re.sub(r'\s\s+', "", teaser)