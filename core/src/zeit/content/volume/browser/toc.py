# -*- coding: utf-8 -*-

from collections import OrderedDict, defaultdict
from io import StringIO
from zeit.cms.browser.interfaces import IPreviewURL
from zeit.cms.i18n import MessageFactory as _
import csv
import os.path
import re
import sys
import zeit.cms.browser.view
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.connector.connector
import zope.app.appsetup.product
import zope.component
import zope.site.site


class Toc(zeit.cms.browser.view.Base):

    CSV_DELIMITER = '\t'

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        filename = self._generate_file_name()
        self.request.response.setHeader('Content-Type', 'text/csv')
        self.request.response.setHeader(
            'Content-Disposition', 'attachment; filename="%s"' % filename)
        return self._create_toc_content()

    def _fill_template(self, text):
        dummy = zeit.content.volume.volume.Volume()
        dummy.year = self.context.year
        dummy.volume = self.context.volume
        return dummy.fill_template(text)

    def _generate_file_name(self):
        toc_file_string = _("Table of Content").lower().replace(" ", "_")
        volume_formatted = self._fill_template("{year}_{name}")
        return "{}_{}.csv".format(toc_file_string, volume_formatted)

    def _create_toc_content(self):
        toc_data = self._get_ir_content()
        sorted_toc_data = self._sort_toc_data(toc_data)
        return self._create_csv(sorted_toc_data)

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
                toc_entry = self._create_toc_element(article)
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

    @property
    def product_ids(self):
        """ List [First Product ID, Second ...] """
        config = zope.app.appsetup.product \
            .getProductConfiguration('zeit.content.volume')
        ids_as_string = config.get('toc-product-ids')
        return [product_id.strip() for product_id in ids_as_string.split(' ')]

    def _create_toc_element(self, article):
        """
        :param article: IArticle
        :return: {'page': int, 'title': str, 'teaser': str, 'supertitle':
        str, 'access': bool, 'authors': str, 'article_id': str}
        """
        toc_entry = self._get_metadata_from_article(article)
        return toc_entry if self._is_relevant(toc_entry) else None

    def _get_metadata_from_article(self, article):
        """
        Get all relevant normalized metadata from article xml tree.
        :param article: IArticle
        :return: {'page': int, 'title': str, 'teaser': str, 'supertitle': str,
        'access': bool, 'authors': str, 'article_id': str}
        """
        result = {
            'title': article.title,
            'page': str(article.page),
            'teaser': article.subtitle,
            'supertitle': article.supertitle,
            'access': article.access,
            'authors': ', '.join([
                x.target.display_name for x in article.authorships]),
            'article_id': article.ir_article_id,
        }
        return self._normalize_toc_element(result)

    REQUIRED = ['title', 'teaser']
    EXCLUDE = {
        'title': [re.compile(x, re.IGNORECASE) for x in [
            'Heute \\d+.\\d+',
            'Damals \\d+.\\d+',
            'PROMINENT IGNORIERT',
            'Du siehst aus, wie ich mich fühle',
            'WAS MEIN LEBEN REICHER MACHT',
            'UND WER BIST DU?'

        ]],
        'supertitle': [re.compile(x, re.IGNORECASE) for x in [
            'NEIN. QUARTERLY',
            'MAIL AUS:',
            'MACHER UND MÄRKTE',
            'AUTO WOFÜR IST DAS DA',
            'HALBWISSEN',
            'ZAHL DER WOCHE',
            'WIR RATEN (AB|ZU)',
            'DER UNNÜTZE VERGLEICH',
            'MALEN NACH ZAHLEN',
            'LEXIKON DER NEUROSEN',
            'ZEITSPRUNG',
            '(LESE|BASTEL)-TIPP'
        ]],
    }

    @classmethod
    def _is_relevant(cls, toc_entry):
        """
        Check, if toc_entry could be an relevant entry.
        :param toc_entry:  {'page': int, 'title': str, 'teaser': str,
        'supertitle': str,''access': bool}
        :return: bool
        """
        have_required = False
        for key in cls.REQUIRED:
            value = toc_entry.get(key)
            if value and not value[0].isspace():
                have_required = True
                break
        if not have_required:
            return False

        for key, matchers in cls.EXCLUDE.items():
            value = toc_entry.get(key)
            if not value:
                continue
            if any(re.match(x, value) for x in matchers):
                return False
        return True

    def _normalize_toc_element(self, toc_entry):
        for key, value in toc_entry.items():
            toc_entry[key] = value.replace(
                self.CSV_DELIMITER, '') if value else ''
        self._normalize_teaser(toc_entry)
        self._normalize_page(toc_entry)
        self._normalize_access_element(toc_entry)
        return toc_entry

    def _normalize_page(self, toc_entry):
        """Transform page to correct integer"""
        page_entries = [x.lstrip("0") for x in re.findall(
            r'\d+', toc_entry.get('page', ''))]
        try:
            page = int(page_entries[0])
        except (IndexError, ValueError):
            page = sys.maxsize
        toc_entry['page'] = page

    def _normalize_teaser(self, toc_entry):
        """Delete linebreaks and a too much whitespace"""
        teaser = toc_entry.get('teaser', '')
        toc_entry['teaser'] = teaser.replace('\n', ' ')
        toc_entry['teaser'] = re.sub(r'\s\s+', ' ', teaser)

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
        file_content = ''
        out = StringIO()
        try:
            writer = csv.writer(out, delimiter=self.CSV_DELIMITER)
            for toc_element in self._generate_csv_rows(toc_data):

                writer.writerow([val for val in toc_element])

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
            [ressort_name, str(self.context.year), str(self.context.volume),
                product_name, toc_entry.get('authors', ''),
                toc_entry.get('article_id', '')])


PRODUCTS = zeit.cms.content.sources.PRODUCT_SOURCE(None)
