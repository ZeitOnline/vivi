# -*- coding: utf-8 -*-

from collections import OrderedDict, defaultdict
from six import StringIO, ensure_str
from zeit.cms.browser.interfaces import IPreviewURL
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.repository.interfaces import IFolder
from zeit.connector.interfaces import IConnector
from zeit.content.article.interfaces import IArticle
from zeit.content.volume.interfaces import ITocConnector
import contextlib
import csv
import os.path
import re
import six.moves.urllib.parse
import sys
import zeit.cms.browser.view
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.connector.connector
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
        self.dav_archive_url_parsed = six.moves.urllib.parse.urlparse(
            self.dav_archive_url)
        self.excluder = Excluder()
        # We need to remember our context DAV properties, as we can't get to
        # them after we change IConnector to ITocConnector. But since we only
        # need year+volume (for fill_template), we can get away with this.
        self._context_year = self.context.year
        self._context_volume = self.context.volume
        self.connector = zope.component.getUtility(ITocConnector)

    @contextlib.contextmanager
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

        old_site = zope.component.hooks.getSite()
        zope.component.hooks.setSite(site)
        yield
        zope.component.hooks.setSite(old_site)

    def __call__(self):
        filename = self._generate_file_name()
        self.request.response.setHeader('Content-Type', 'text/csv')
        self.request.response.setHeader(
            'Content-Disposition', 'attachment; filename="%s"' % filename)
        return self._create_toc_content()

    def _fill_template(self, text):
        dummy = zeit.content.volume.volume.Volume()
        dummy.year = self._context_year
        dummy.volume = self._context_volume
        return dummy.fill_template(text)

    def _generate_file_name(self):
        toc_file_string = _("Table of Content").lower().replace(" ", "_")
        volume_formatted = self._fill_template("{year}_{name}")
        return "{}_{}.csv".format(toc_file_string, volume_formatted)

    def _create_toc_content(self):
        """
        Create Table of Contents for the given Volume as a csv.
        :return: str - Table of content csv string
        """
        with self._register_archive_connector():
            toc_data = self._get_k4_content()
        ir_data = self._get_ir_content()
        self._merge_ir_into_k4(toc_data, ir_data)
        sorted_toc_data = self._sort_toc_data(toc_data)
        return self._create_csv(sorted_toc_data)

    def _get_k4_content(self):
        """
        Get and parse xml form webdav und create toc entries.
        :return: OrderedDict of Toc entries.
        Sorted like toc-product-ids given list in the product config.
        {
        'Product Name':
            {
            'Ressort' :
                [{'page': int, 'title': str, 'teaser': str, 'supertitle':
                str, 'access': bool},
                ...]
            }
        }
        """
        results = OrderedDict()
        for product in self.product_ids:
            result_for_product = {}
            product_folder = self._fill_template(
                'http://xml.zeit.de/%s/{year}/{name}/' % product)
            for ressort_folder in self.list_relevant_ressort_folders(
                    product_folder):
                result_for_ressort = []
                for article in self._get_all_article_elements(ressort_folder):
                    toc_entry = self._create_toc_element(article)
                    if toc_entry:
                        result_for_ressort.append(toc_entry)
                ressort_folder_name = ressort_folder.__name__ \
                    .replace('-', ' ').title()
                result_for_product[ressort_folder_name] = result_for_ressort
            results[self._full_product_name(product)] = result_for_product
        return results

    MEDIASYNC_ID = ('mediasync_id', 'http://namespaces.zeit.de/CMS/interred')

    def _get_ir_content(self):
        results = {}
        for product in self.product_ids:
            product = PRODUCTS.find(product)
            if not product or not product.location:
                continue
            result_for_product = defaultdict(list)
            product_folder = os.path.dirname(
                self._fill_template(product.location))
            product_folder = zeit.cms.interfaces.ICMSContent(
                product_folder, None)
            if product_folder is None:
                continue
            for article in product_folder.values():
                props = zeit.connector.interfaces.IWebDAVProperties(article)
                if self.MEDIASYNC_ID not in props:
                    continue
                toc_entry = self._create_toc_element(article.xml)
                if toc_entry:
                    if (article.main_image and
                            article.main_image.target is not None):
                        toc_entry['image_url'] = self.url(
                            article.main_image.target)
                    toc_entry['preview_url'] = zope.component.getMultiAdapter(
                        (article, 'preview'), IPreviewURL)
                    result_for_product[article.printRessort].append(toc_entry)
            results[product.title] = result_for_product
        return results

    def _merge_ir_into_k4(self, k4_data, ir_data):
        for product, ir_product in ir_data.items():
            k4_product = k4_data[product]
            for name, ir_ressort in ir_product.items():
                k4_ressort = k4_product.setdefault(name, [])
                k4_ressort.extend(ir_ressort)

    @property
    def product_ids(self):
        """ List [First Product ID, Second ...] """
        config = zope.app.appsetup.product \
            .getProductConfiguration('zeit.content.volume')
        ids_as_string = config.get('toc-product-ids')
        return [product_id.strip() for product_id in ids_as_string.split(' ')]

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
        return (IFolder.providedBy(item[1]) and
                self.excluder.is_relevant_folder(item[0]))

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
        :return: {'page': int, 'title': str, 'teaser': str, 'supertitle':
        str, 'access': bool, 'authors': str, 'article_id': str}
        """
        toc_entry = self._get_metadata_from_article_xml(article_element)
        if self._is_sane(toc_entry) and self.excluder.is_relevant(
                article_element):
            return toc_entry
        else:
            return None

    def _get_metadata_from_article_xml(self, atricle_tree):
        """
        Get all relevant normalized metadata from article xml tree.
        :param atricle_tree: lxml.etree Element
        :return: {'page': int, 'title': str, 'teaser': str, 'supertitle': str,
        'access': bool, 'authors': str, 'article_id': str}
        """
        xpaths = {
            'title': "body/title/text()",
            'page': "//attribute[@name='page']/text()",
            'teaser': "body/subtitle/text()",
            'supertitle': "body/supertitle/text()",
            'access': "//attribute[@name='access']/text()",
            'authors': "//attribute[@name='author']/text()",
            'article_id': "//attribute[@name='article_id']/text()"
        }
        res = {}
        for key, xpath in xpaths.items():
            res[key] = atricle_tree.xpath(xpath)
        return self._normalize_toc_element(res)

    def _is_sane(self, toc_entry):
        """
        Check, if toc_entry could be an relevant entry.
        :param toc_entry:  {'page': int, 'title': str, 'teaser': str,
        'supertitle': str,''access': bool}
        :return: bool
        """
        required_entries = ['title', 'teaser']
        for entry in required_entries:
            value = toc_entry.get(entry)
            if value and not value[0].isspace():
                return True
        return False

    def _normalize_toc_element(self, toc_entry):
        for key, value in toc_entry.items():
            toc_entry[key] = value[0].replace(self.CSV_DELIMITER, '') \
                if len(value) > 0 else u""
        self._normalize_teaser(toc_entry)
        self._normalize_page(toc_entry)
        self._normalize_access_element(toc_entry)
        return toc_entry

    def _normalize_page(self, toc_entry):
        """Transform page to correct integer"""
        page_entries = [x.lstrip("0") for x in re.findall(
            r'\d+', toc_entry.get('page', u''))]
        try:
            page = int(page_entries[0])
        except (IndexError, ValueError):
            page = sys.maxsize
        toc_entry['page'] = page

    def _normalize_teaser(self, toc_entry):
        """Delete linebreaks and a too much whitespace"""
        teaser = toc_entry.get('teaser', u'')
        toc_entry['teaser'] = teaser.replace('\n', u' ')
        toc_entry['teaser'] = re.sub(r'\s\s+', u' ', teaser)

    def _normalize_access_element(self, toc_entry):
        if not toc_entry['access']:
            toc_entry['access'] = "Nicht Gesetzt"
        else:
            toc_entry['access'] = \
                zeit.cms.content.sources.ACCESS_SOURCE.factory.getTitle(
                self.context, toc_entry['access'])

    def _full_product_name(self, product_id):
        product = PRODUCTS.find(product_id)
        if not product:
            return product_id
        return product.title

    def _sort_toc_data(self, toc_data):
        """
        Sort the toc data dict.
        :param toc_data: Table of content data as dict.
        :return: OrderedDict
        """
        for product_name, ressort_dict in toc_data.items():
            for ressort_name, articles in ressort_dict.items():
                toc_data[product_name][ressort_name] = \
                    sorted(articles, key=lambda x: x.get('page', sys.maxsize))
        for product_name, ressort_dict in toc_data.items():
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
        for resort_name, articles in ressorts.items():
            # Empty ressorts should be listed as last entries in toc
            min_page = sys.maxsize
            if articles:
                min_page = articles[0].get('page', sys.maxsize)
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
        out = StringIO()
        try:
            writer = csv.writer(out, delimiter=self.CSV_DELIMITER)
            for toc_element in self._generate_csv_rows(toc_data):

                writer.writerow(
                    [ensure_str(val) for val in toc_element]
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
        for product_name, ressort_dict in toc_entries.items():
            for ressort_name, toc_entries in ressort_dict.items():
                for toc_entry in toc_entries:
                    yield self._format_toc_element(
                        toc_entry, product_name, ressort_name)
        return

    def _format_toc_element(self, toc_entry, product_name, ressort_name):
        title_teaser = " ".join(
            [toc_entry.get("title"),
             toc_entry.get("teaser")])
        page = toc_entry.get('page')
        if page == sys.maxsize:
            page = ''
        return (
            [str(page), title_teaser, '', '', toc_entry.get('access')] +
            [''] * 8 + [toc_entry.get('image_url', '')] +
            [''] * 5 + [toc_entry.get('preview_url', '')] +
            [ressort_name, str(self._context_year), str(self._context_volume),
                product_name, toc_entry.get('authors', ''),
                toc_entry.get('article_id', '')])


PRODUCTS = zeit.cms.content.sources.PRODUCT_SOURCE(None)


class Excluder(object):
    """
    Checks if an article should be excluded from the table of contents.
    """
    # Rules should be as strict as possible,
    # otherwise the wrong article might get excluded
    TITLE_XPATH = "body/title/text()"
    SUPERTITLE_XPATH = "body/supertitle/text()"
    JOBNAME_XPATH = "//attribute[@name='jobname']/text()"
    _title_exclude = [
        u"Heute \\d+.\\d+",
        u"Damals \\d+.\\d+",
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
        u'(Mail |AS-Zahl|Impressum)'
    ]

    def __init__(self):
        self._compiled_title_regexs = [re.compile(r, re.IGNORECASE)
                                       for r in self._title_exclude]
        self._compiled_supertitle_regexs = [re.compile(r, re.IGNORECASE)
                                            for r in self._supertitle_exclude]
        self._compiled_jobname_regexs = [re.compile(r, re.IGNORECASE)
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
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.content.volume')
    dav_archive_url = config.get('dav-archive-url')
    return zeit.connector.connector.TransactionBoundCachingConnector(
        {'default': dav_archive_url})
