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
import zeit.cms.interfaces
from zeit.cms.repository.interfaces import IFolder
import zeit.connector.connector
from zeit.connector.interfaces import IConnector
from zeit.content.article.interfaces import IArticle
from zeit.content.volume.interfaces import ITocConnector, PRODUCT_MAPPING

import zope.app.appsetup.product
import zope.component
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

    def __init__(self, context, request):
        self.context = context
        self.request = request
        config = zope.app.appsetup.product \
            .getProductConfiguration('zeit.content.volume')
        self.dav_archive_url = config.get('dav-archive-url')
        self.dav_archive_url_parsed = urlparse.urlparse(self.dav_archive_url)
        self.excluder = Excluder()
        self.connector = zope.component.getUtility(ITocConnector)
        self._register_archive_connector()

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
        registry.registerUtility(self.connector, IConnector)
        zope.component.hooks.setSite(site)

    def __call__(self):
        filename = self._generate_file_name()
        self.request.response.setHeader('Content-Type', 'text/csv')
        self.request.response.setHeader(
            'Content-Disposition', 'attachment; filename="%s"' % filename)
        return self._create_toc_content()

    def _generate_file_name(self):
        toc_file_string = _("Table of Content").lower().replace(" ", "_")
        volume_formatted = self.context.fill_template("{year}_{name}")
        return "{}_{}.csv".format(toc_file_string, volume_formatted)

    def _create_toc_content(self):
        """
        Create Table of Contents for the given Volume as a csv.
        :return: str - Table of content csv string
        """
        toc_data = self._get_via_dav()
        sorted_toc_data = self._sort_toc_data(toc_data)
        return self._create_csv(sorted_toc_data)

    def _get_via_dav(self):
        """
        Get and parse xml form webdav und create toc entries.
        :return: OrderedDict of Toc entries.
        Sorted like toc-product-ids given list in the product config.
        {
        'Product Name':
            {
            'Ressort' :
                [{'page': int, 'title': str, 'teaser': str, 'author': str},...]
            }
        }
        """
        results = OrderedDict()
        for prod_uid in self._get_product_uids():
            result_for_product = {}
            for ressort_folder in self.list_relevant_ressort_folders(prod_uid):
                result_for_ressort = []
                for article in self._get_all_article_elements(ressort_folder):
                    toc_entry = self._create_toc_element(article)
                    if toc_entry:
                        result_for_ressort.append(toc_entry)
                ressort_folder_name = ressort_folder.__name__ \
                    .replace('-', ' ').title()
                result_for_product[ressort_folder_name] = result_for_ressort
            results[self._full_product_name(prod_uid)] = result_for_product
        return results

    @property
    def product_ids(self):
        """ List [First Product ID, Second ...] """
        config = zope.app.appsetup.product \
            .getProductConfiguration('zeit.content.volume')
        ids_as_string = config.get('toc-product-ids')
        return [product_id.strip() for product_id in ids_as_string.split(' ')]

    def _get_product_uids(self):
        """
        Creates a list of uids to all given products.
        :param product_ids: [str]
        :return: [str]
        """
        return [self.context.fill_template(
            'http://xml.zeit.de/%s/{year}/{name}/' % x) for x in
                self.product_ids]

    def list_relevant_ressort_folders(self, product_uid):
        """
        :param product_uid: uid to product for the volume
        :return: [zeit.cms.repository.folder.Folder, ...]
        """
        try:
            product_folder = \
                zeit.cms.interfaces.ICMSContent(self.connector[product_uid])
            return [item[1] for item in product_folder.items()
                    if self._is_relevant_folder_item(item)]
        except KeyError:
            return []

    def _is_relevant_folder_item(self, item):
        return IFolder.providedBy(item[1])and \
               self.excluder.is_relevant_folder(item[0])

    def _get_all_article_elements(self, ressort_folder):
        """
        Returns lxml-Objects for all Articles in ressort_folder.
        Using the adapted IArticle doesn't work due to some difference in
        the page xml element, which can't be parsed the normal way.
        :return: [lxml.etree Article element, ...]
        """
        return [resource.xml for resource in ressort_folder.values()
                if IArticle.providedBy(resource)]

    def _create_toc_element(self, article_element):
        """
        :param article_element: lxml.etree Article element
        :return: {'page': int, 'author': str, 'title': str, 'teaser': str}
        """
        return self._get_metadata_from_article_xml(article_element) \
            if self.excluder.is_relevant(article_element) else None

    def _get_metadata_from_article_xml(self, atricle_tree):
        """
        Get all relevant normalized metadata from article xml tree.
        :param atricle_tree: lxml.etree Element
        :return: {'page': int, 'author': str, 'title': str, 'teaser': str}
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
        """Transform page to correct integer"""
        page_string = toc_dict.get('page', u'')
        res = re.findall('\d+', page_string)
        if res:
            page = int(res[0].lstrip("0"))
        else:
            page = sys.maxint
        toc_dict['page'] = page

    def _normalize_teaser(self, toc_entry):
        """Delete linebreaks and a too much whitespace"""
        teaser = toc_entry.get('teaser', u'')
        toc_entry['teaser'] = teaser.replace('\n', u' ')
        toc_entry['teaser'] = re.sub(r'\s\s+', u' ', teaser)

    def _full_product_name(self, product_uid):
        """
        :param product_uid: str -  /PRODUCT_ID/YEAR/VOL/
        """
        splitted_path = product_uid.split(posixpath.sep)
        product_id = splitted_path[-4]
        return PRODUCT_MAPPING.get(product_id, product_id)

    def _sort_toc_data(self, toc_data):
        """
        Sort the toc data dict.
        :param toc_data: Table of content data as dict.
        :return: OrderedDict
        """
        for product_name, ressort_dict in toc_data.iteritems():
            for ressort_name, articles in ressort_dict.iteritems():
                toc_data[product_name][ressort_name] = \
                    sorted(articles, key=lambda x: x.get('page', sys.maxint))
        for product_name, ressort_dict in toc_data.iteritems():
            toc_data[product_name] = self._sorted_ressorts(ressort_dict)
        return toc_data

    def _sorted_ressorts(self, ressorts):
        """
        Ressort dicts will be sorted by min page of its articles.
        Expects articles in ressorts dict to be sorted by page.
        :param ressorts: {RESSORTNAME: [ARTICLES AS DICT]}
        :return: OrderedDict
        """
        ressort_min_page_number_tuples = []
        for resort_name, articles in ressorts.iteritems():
            # Empty ressorts should be listed as last entries in toc
            min_page = sys.maxint
            if articles:
                min_page = articles[0].get('page', sys.maxint)
            ressort_min_page_number_tuples.append((resort_name, min_page))
        d = OrderedDict()
        for ressort_page_tuple in sorted(
                ressort_min_page_number_tuples, key=lambda resort_page_tup:
                resort_page_tup[1]):
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
        page = toc_entry.get('page')
        if page == sys.maxint:
            page = ''
        return [str(page), toc_entry.get("author"),
                title_teaser]


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
        """Checks if a folder is on the blacklist."""
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
