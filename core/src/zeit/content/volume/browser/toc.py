# -*- coding: utf-8 -*-
import StringIO
import csv
import urlparse
import re
import sys
import posixpath
from ordereddict import OrderedDict

import zeit.cms.browser.view
from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.sources
import zeit.cms.interfaces
from zeit.cms.repository.interfaces import IFolder
import zeit.connector.connector
from zeit.connector.interfaces import IConnector
from zeit.content.article.interfaces import IArticle
from zeit.content.volume.interfaces import ITocConnector

import zope.app.appsetup.product
import zope.component
import zope.component.registry
import zope.interface
import zope.site.site


class Toc(zeit.cms.browser.view.Base):
    """
    View for creating a Table of Content as a csv file.
    The dav url to the articles generally looks like
    ARCHIVE_ROOT/PRODUCT_ID/RESSORT_NAME/ARTICLE.xml
    E.g.
    cms-backend.zeit.de/cms/archiv-wf/archiv/ZEI/2016/23/entdecken/03-Normalo
    """
    CSV_DELIMITER = '\t'

    def __init__(self, *args, **kwargs):
        super(Toc, self).__init__(*args, **kwargs)

        config = zope.app.appsetup.product \
            .getProductConfiguration('zeit.content.volume')
        self.dav_archive_url = config.get('dav-archive-url')
        self.dav_archive_url_parsed = urlparse.urlparse(self.dav_archive_url)
        self.excluder = Excluder()
        self._register_archive_connector()
        self.connector = zope.component.getUtility(ITocConnector)

    def _register_archive_connector(self):
        """
        Due to the need of using another section of the WebDAV-Server(
        /cms/wf-archiv...) a new
        IConnector has to be registered, otherwise the
        cms.repository.Repository could not be used afterwards.
        """
        default_registry = zope.component.getSiteManager()
        site = zope.site.site.SiteManagerContainer()
        registry = zope.site.site.LocalSiteManager(site, default_folder=False)
        registry.__bases__ = (default_registry,)
        # New registry has to removed as a sub from the base registry,
        # because otherwise the base registry has a reference on the new one.
        # This would make the new registry persistent.
        default_registry.removeSub(registry)
        site.setSiteManager(registry)
        connector = zope.component.getUtility(ITocConnector)
        registry.registerUtility(connector, IConnector)
        zope.component.hooks.setSite(site)

    def __call__(self):
        self.product_id_mapping = self._create_product_id_full_name_mapping()
        filename = self._generate_file_name()
        self.request.response.setHeader('Content-Type', 'text/csv')
        self.request.response.setHeader(
            'Content-Disposition', 'attachment; filename="%s"' % filename)
        return self._create_toc_content()

    def _create_product_id_full_name_mapping(self):
        products = list(zeit.cms.content.sources.PRODUCT_SOURCE(self.context))
        return dict([(product.id, product.title) for product in products])

    def _generate_file_name(self):
        toc_file_string = _("Table of Content").lower().replace(" ", "_")
        volume_formatted = self.context.fill_template("{year}_{name}")
        return "{}_{}.csv".format(toc_file_string, volume_formatted)

    def _create_toc_content(self):
        """
        Create Table of Contents for the given Volume as a csv.
        :param volume: ..volume.Volume Content Instance
        :return: str - Table of content csv string
        """
        toc_data = self._get_via_dav()
        sorted_toc_data = self._sort_toc_data(toc_data)
        return self._create_csv(sorted_toc_data)

    def _get_via_dav(self):
        """
        Get and parse xml form webdav und create toc entries.
        :param volume: ..volume.Volume Instance
        :return: Sorted Dict of Toc entries.
        Sorted like toc-product-ids given list in the product config.
        {
        'Product Name':
            {
            'Ressort' :
                [{'page': str, 'title': str, 'teaser': str, 'author': str},...]
            }
        }
        """
        results = OrderedDict()
        for product_path in self._get_all_paths_for_product_ids():
            result_for_product = {}
            for ressort_folder_name, ressort_folder in \
                    self.list_relevant_ressort_folders(product_path):
                result_for_ressort = []
                for article_element in \
                        self._get_all_article_elements(ressort_folder):
                    toc_entry = self._create_toc_element(article_element)
                    if toc_entry:
                        result_for_ressort.append(toc_entry)
                ressort_folder_name = ressort_folder_name.replace('-', ' ') \
                    .title()
                result_for_product[ressort_folder_name] = result_for_ressort
            results[self._full_product_name(product_path)] = result_for_product
        return results

    @property
    def product_ids(self):
        """ List [First Product ID, Second ...] """
        config = zope.app.appsetup.product\
                .getProductConfiguration('zeit.content.volume')
        ids_as_string = config.get('toc-product-ids')
        return [product_id.strip() for product_id in ids_as_string.split(' ')]

    def _get_all_product_ids_for_volume(self):
        """ List [First Product ID, Second ...] """
        # Change it if the volume content object "knows" which Products it has
        config = zope.app.appsetup.product \
            .getProductConfiguration('zeit.content.volume')
        ids_as_string = config.get('toc-product-ids')
        return [product_id.strip() for product_id in ids_as_string.split(' ')]

    def _get_all_paths_for_product_ids(self):
        """
        Creates a list of unix-paths to all given products
        :param product_ids: [str]
        :return: [str]
        """
        # Volumes <10 would lead to wrong paths like YEAR/1 instead of YEAR/01
        volume_string = '%02d' % self.context.volume
        # You need the XML prefix here
        prefix = 'http://xml.zeit.de'
        return [posixpath.join(*[str(e) for e in
                                 [prefix, dir_name, self.context.year, volume_string, '']])
                for dir_name in self.product_ids]

    def list_relevant_ressort_folders(self, path):
        """
        :param path: path to product for the volume
        :return: [('foldername', zeit.cms.repository.folder.Folder), ...]
        """
        try:
            product_folder = \
                zeit.cms.interfaces.ICMSContent(self.connector[path])
            return [item for item in product_folder.items()
                    if self._is_relevant_folder_item(item)]
        except KeyError:
            return []

    def _is_relevant_folder_item(self, item):
        return self.excluder.is_relevant_folder(item[0]) \
               and IFolder.providedBy(item[1])

    def _get_all_article_elements(self, ressort_folder):
        """
        Get all DAV Server paths to article files in path.
        :param ressort_folder:
        :return: [lxml.etree Article element, ...]
        """
        return [resource.xml for _, resource in ressort_folder.items()
                if IArticle.providedBy(resource)]

    def _create_toc_element(self, article_element):
        """
        :param article_element: lxml.etree Article element
        :return: {'page': str, 'author': str, 'title': str, 'teaser': str}
        """
        return self._get_metadata_from_article_xml(article_element) \
            if self.excluder.is_relevant(article_element) else None

    def _get_metadata_from_article_xml(self, atricle_tree):
        """
        Get all relevant normalized metadata from article xml tree.
        Using the adapted IArticle doesn't work due to some difference in
        the page xml element, which can't be parsed.
        :param atricle_tree: lxml.etree Element
        :return: {'page': str, 'author': str, 'title': str, 'teaser': str}
        """
        xpaths = {
            'title': "body/title/text()",
            'page': "//attribute[@name='page']/text()",
            'teaser': "body/subtitle/text()",
            'author': "//attribute[@name='author']/text()"
        }
        res = {}
        for key, xpath in xpaths.iteritems():
            res[key] = atricle_tree.xpath(xpath)
        return self._normalize_toc_element(res)

    def _normalize_toc_element(self, toc_entry):
        for key, value in toc_entry.iteritems():
            toc_entry[key] = value[0].replace(self.CSV_DELIMITER, '') \
                if len(value) > 0 else u""
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

    def _full_product_name(self, product_path):
        """
        :param product_path: str -  /PRODUCT_ID/YEAR/VOL/
        """
        splitted_path = product_path.split(posixpath.sep)
        product_id = splitted_path[-4]
        return self.product_id_mapping.get(product_id, product_id)

    def _sort_toc_data(self, toc_data):
        """
        Sort the toc data dict
        :param toc_data:
        :return: OrderedDict
        """
        for product_name, ressort_dict in toc_data.iteritems():
            for ressort_name, articles in ressort_dict.iteritems():
                toc_data[product_name][ressort_name] = \
                    sorted(articles, key=self._get_page_from_article)
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
            # The empty string will raise a Value Error
            return sys.maxint

    def _sorted_ressorts(self, ressorts):
        """
        Ressort dicts will be sorted by min page of its articles.
        Expects articles in ressorts dict to be sorted by page
        :param ressorts: {RESSORTNAME: [ARTICLES AS DICT]}
        :return: OrderedDict
        """
        ressort_min_page_number_tuples = []
        for resort_name, articles in ressorts.iteritems():
            # Empty ressorts should be listed as last entries in toc
            min_page = sys.maxint
            if articles:
                min_page = self._get_page_from_article(articles[0])
            ressort_min_page_number_tuples.append((resort_name, min_page))
        d = OrderedDict()
        for ressort_page_tuple in sorted(
                ressort_min_page_number_tuples, key=lambda
                        resort_page_tup: resort_page_tup[1]):
            d[ressort_page_tuple[0]] = ressorts.get(ressort_page_tuple[0])
        return d

    def _create_csv(self, toc_data):
        """
        Creates CSV File from TOC Data.
        SEITENZAHL [tab] AUTOREN [tab] TITEL + TEASER
        :param toc_data: The Toc data as ordered dict.
        :return: unicode - csv content
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
        :param toc_entries - The Toc data as ordered dict.
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
        title_teaser = \
            toc_entry.get("title") + u" " + toc_entry.get("teaser")
        return [toc_entry.get("page"), toc_entry.get("author"), title_teaser]


class Excluder(object):
    """
    Checks if an article should be excluded from the table of contents.
    """
    # Rules should be as strict as possible,
    # otherwise the wrong article might get  excluded
    TITLE_XPATH = "body/title/text()"
    SUPERTITLE_XPATH = "body/supertitle/text()"
    JOBNAME_XPATH = "//attribute[@name='jobname']/text()"
    _title_exclude = [
        u"Heute \d+.\d+",
        u"Damals \d+.\d+",
        u"PROMINENT IGNORIERT",
        u"Du siehst aus, wie ich mich fühle",
        u"WAS MEIN LEBEN REICHER MACHT",
        u"UND WER BIST DU?"

    ]
    _supertitle_exclude = [
        u"NEIN. QUARTERLY",
        u"MAIL AUS:",
        u"MACHER UND MÄRKTE",
        u"AUTO WOFÜR IST DAS DA",
        u"HALBWISSEN",
        u"ZAHL DER WOCHE",
        u"WIR RATEN (AB|ZU)",
        u"DER UNNÜTZE VERGLEICH",
        u"MALEN NACH ZAHLEN",
        u"LEXIKON DER NEUROSEN",
        u"ZEITSPRUNG",
        u"(LESE|BASTEL)-TIPP"
    ]

    _jobname_exclude = [
        u'(Traumstück|AS-Zahl)'
    ]

    def __init__(self):
        self._compiled_title_regexs = [re.compile(r)
                                       for r in self._title_exclude]
        self._compiled_supertitle_regexs = [re.compile(r)
                                            for r in self._supertitle_exclude]
        self._compiled_jobname_regexs = [re.compile(r)
                                         for r in self._jobname_exclude]

    def is_relevant(self, article_lxml_tree):
        # TODO A lot of Code repetition
        title_values = article_lxml_tree.xpath(self.TITLE_XPATH)
        supertitle_values = article_lxml_tree.xpath(self.SUPERTITLE_XPATH)
        jobname_values = article_lxml_tree.xpath(self.JOBNAME_XPATH)

        title_value = title_values[0] \
            if len(title_values) > 0 else ''
        supertitle_value = supertitle_values[0] \
            if len(supertitle_values) > 0 else ''
        jobname_value = jobname_values[0] if len(jobname_values) > 0 else ''

        title_exclude = any(
            [re.match(title_pattern, title_value)
             for title_pattern in self._compiled_title_regexs]
        )
        supertitle_exclude = any(
            [re.match(supertitle_pattern, supertitle_value)
             for supertitle_pattern in self._compiled_supertitle_regexs]
        )
        jobname_exclude = any(
            [re.match(jobname_pattern, jobname_value)
             for jobname_pattern in self._compiled_jobname_regexs]
        )
        return not(title_exclude or supertitle_exclude or jobname_exclude)

    def is_relevant_folder(self, folder_path):
        folders_to_exclude = {'images', 'leserbriefe'}
        folders_to_exclude = set.union(
            folders_to_exclude,
            {ele.title() for ele in folders_to_exclude})
        return not any(folder in folder_path for folder in folders_to_exclude)


def toc_connector_factory():
    config = zope.app.appsetup.product\
            .getProductConfiguration('zeit.content.volume')
    dav_archive_url = config.get('dav-archive-url')
    return zeit.connector.connector.TransactionBoundCachingConnector(
            {'default': dav_archive_url})
