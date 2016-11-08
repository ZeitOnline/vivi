# -*- coding: utf-8 -*-
import StringIO
import csv
import urlparse
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
import toc_config
import zope.app.appsetup.product

# TODO Author/Title Teaser contains is ugly
# TODO More Abstraction of Toc Entries, not sure if an ordered dict is a great idea
#

"""
TODO: Nachfragen "Die Product-Config ist leider untypisiert (also nur Strings); an anderen Stellen benutzten wir deshalb Leerzeichen als Trenner."
Heißt dass, das soll auch in einer Config stehen, oder lass das mal drin aber satt ner Liste nimm einen String,
der dann gesplitet wird?

Jep, unbedingt. :) Die Doku zum Konfigurationsmechanismus ist auch ungelogen ;) der nächste Punkt auf meiner "sollte man dokumentieren" Liste.
Die Kurzfassung ist:
https://github.com/ZeitOnline/zeit.retresco/blob/master/src/zeit/retresco/connection.py#L180
https://github.com/zeitonline/vivi-deployment/blob/master/components/zope/zope.conf#L254
https://github.com/zeitonline/vivi-deployment/blob/master/components/settings/component.py#L148
https://github.com/zeitonline/vivi-deployment/blob/master/environments/production.cfg#L75, https://github.com/zeitonline/vivi-deployment/blob/master/environments/staging.cfg#L78 etc.
# TODO hier checke ich nicht, warum ich die nicht finde, und wie das von den enviorenments da rein kommt.
# Muss ich das dann nach einer Änderung noch einmal neu deployen?

Das kann man mit nem Format-String schöner schreiben (volume_string = '%02d' % self.context.volume)


So generell zu dieser Klasse: ich find beim Lesen irgendwie nie die Methode, die ich suche. ;) Als typische Ordnung find ich hilfreich, die "wichtigen" oder "Einstiegspunkte" zuoberst, und dann unterhalb jeder Funktion halt die Hilfsfunktionen, die dort aufgerufen werden -- insbesondere wenn die Hilfsfunktionen vor allem der Gliederung und Benamsung dienen (und nicht unbedingt an verschiedenen Stellen aufgerufen werden).


Also just diese Eigenschaften sind zu dieser Stufe des Print-Imports schon im von vivi erwarteten Format vorhanden, insofern könnte man überlegen, statt von Hand parsen einen z.c.article.article.Article(xml_file_pointer) zu verwenden.

Also von der Bedienung her wär es schon deutlich bequemer, wenn man zeit.cms.repository.folder.Folder und Co verwenden würde...

Ich find es schon richtig, wenn man ganze Verzeichnisse ignorieren kann, das dann auch zu tun, und nicht erst die Artikel darin noch zu parsen, nur um sie anschließend wegzuwerfen.
Die Einstellung, welche Verzeichnisse wir überspringen, könnte man allerdings tatsächlich vielleicht auf der ArticleExcluder Klasse unterbringen (bzw. längerfristig dann aus der Product-Config holen).

Vermutlich sind die Datenmengen nicht so riesig, aber Zope kann das View-Ergebnis anstatt als String auch direkt aus nem file-like-object zurückgeben, siehe zope.file.download.DownloadResult.

"""


class Toc(zeit.cms.browser.view.Base):
    """
    View for creating a Table of Content as a csv file.
    The dav url to the articles generally looks like ARCHIVE_ROOT/PRODUCT_ID/RESSORT_NAME/ARTICLE.xml
    """
    # Not all directories in the archives are named the product ID.
    PRODUCT_ID_DIR_NAME_EXCEPTIONS = {'CW': 'ZECW'}
    CSV_DELIMITER = '\t'

    def __init__(self, *args, **kwargs):
        super(Toc, self).__init__(*args, **kwargs)
        # Dependency injection?
        self.dav_archive_url_parsed = self._parse_config()
        self.client = self._create_dav_client()
        self.article_excluder = ArticleExcluder()

    def __call__(self):
        self.product_id_mapping = self._create_product_id_full_name_mapping()
        filename = self._generate_file_name()
        self.request.response.setHeader('Content-Type', 'text/csv')
        self.request.response.setHeader(
            'Content-Disposition', 'attachment; filename="%s"' % filename)
        return self._create_toc_content()

    def _parse_config(self):
        """
        Get ARCHIVE_DAV_URL from zope.conf and parse it with.
        :return: urlparse.ParseResult
        """
        # config = zope.app.appsetup.product.getProductConfiguration('zeit.volume')
        # return urlparse.urlparse(config.get('archive-dav-url'))
        return urlparse.urlparse(toc_config.ARCHIVE_DAV_URL)

    def _create_toc_content(self):
        """
        Create Table of Contents for the given Volume as a csv.
        :param volume: ..volume.Volume Content Instance
        :return: str - Table of content csv string
        """
        toc_data = self._get_via_dav()
        sorted_toc_data = self._sort_toc_data(toc_data)
        return self._create_csv(sorted_toc_data)

    def _generate_file_name(self):
        toc_file_string = _("Table of Content").lower().replace(" ", "_")
        volume_formatted = self.context.fill_template("{year}_{name}")
        return "{}_{}.csv".format(toc_file_string, volume_formatted)

    def _get_via_dav(self):
        """
        Get and parse xml form webdav und create toc entries.
        :param volume: ..volume.Volume Content Instance
        :return: Sorted Dict of Toc entries. Sorted like the toc_config.PRODUCT_IDS list.
                 {
                        'Product Name':
                                 {
                                    'Ressort' : [{'page': str, 'title': str, 'teaser': str, 'author': str},...]
                                 }
                 }
        """
        results = OrderedDict()
        product_ids = self._get_all_product_ids_for_volume()
        for product_path in self._get_all_paths_for_product_ids(product_ids):
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
        """
        Get all DAV Server paths to article files in path.
        :param path: str - archive path to ressort, e.g. 'cms/archiv/ws-archiv/ZEI/2016/23/'
        :return: [str]
        """
        all_article_paths = []
        for article_path in self._get_all_files_in_folder(path):
            all_article_paths.append(article_path)
        return all_article_paths

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
        """ Returns List [First Product ID, Second ...] """
        # Change this if the volume content object "knows" which Products it has...
        return toc_config.PRODUCT_IDS

    def _get_all_paths_for_product_ids(self, product_ids):
        """
        Creates a list of unix-paths to all given products
        :param product_ids: [str]
        :return: [str]
        """
        product_dir_names = [self._replace_product_id_by_its_dirname(product_id) for product_id in product_ids]
        # Volumes <10 would lead to wrong paths like YEAR/1 instead of YEAR/01
        volume_string = '%02d' % self.context.volume
        return [posixpath.join(*[str(e) for e in [self.dav_archive_url_parsed.path, dir_name, self.context.year, volume_string, '']])
                for dir_name in product_dir_names]

    def _replace_product_id_by_its_dirname(self, product_id):
        """
        :param product_id: str
        :param reverse: Bool - replace directorynames with product ID's instead.
        :return: str
        """
        return self.PRODUCT_ID_DIR_NAME_EXCEPTIONS.get(product_id, product_id)


    def _is_relevant_article(self, article_tree):
        """
        Predicate to decide if a doc is relevant for the toc.
        :param article_tree: lxml.etree  of the article
        :return: bool
        """
        return self.article_excluder.is_relevant(article_tree)

    def _create_dav_client(self):
        return tinydav.WebDAVClient(self.dav_archive_url_parsed.hostname, self.dav_archive_url_parsed.port)

    def _get_metadata_from_article_xml(self, atricle_tree):
        """
        Get all relevant normalized metadata from article xml tree.
        :param atricle_tree: lxml.etre Element -
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

    def list_relevant_ressort_dirs_with_dav(self, path):
        """ Returns all relevant ressort paths to directories for a given path """
        try:
            response = self.client.propfind(path, depth=1)
            assert response.is_multistatus
            return [element.href for element in response if self._is_relevant_path_to_directory(path, element)]
        except HTTPUserError:
            return []

    def _is_relevant_path_to_directory(self, root_path_of_element, element):
        """

        :param root_path_of_element: root path of DAV archive
        :param element: tinydav status element
        :return: bool
        """
        try:
            # TODO Put this in the excluder ?
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
        Sort the toc data dict
        :param toc_data:
        :return: OrderedDict
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
        for ressort_min_page_tuple in sorted(ressort_min_page_number_tuples, key=lambda resort_page_tup: resort_page_tup[1]):
            d[ressort_min_page_tuple[0]] = ressorts.get(ressort_min_page_tuple[0])
        return d


class ArticleExcluder(object):
    """
    Checks if an article should be excluded from the table of contents.
    """
    # Rules should be as strict as possible, otherwise the wrong article might get  excluded
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
        # TODO Create combined regex? Should be faster.
        # compile regexes for article
        self._compiled_title_regexs = [re.compile(regex) for regex in self._title_exclude]
        self._compiled_supertitle_regexs = [re.compile(regex) for regex in self._supertitle_exclude]
        self._compiled_jobname_regexs = [re.compile(regex) for regex in self._jobname_exclude]

    def is_relevant(self, article_lxml_tree):
        # TODO A lot of Code repetition
        title_values = article_lxml_tree.xpath(self.TITLE_XPATH)
        supertitle_values = article_lxml_tree.xpath(self.SUPERTITLE_XPATH)
        jobname_values = article_lxml_tree.xpath(self.JOBNAME_XPATH)

        title_value = title_values[0] if len(title_values) > 0 else ''
        supertitle_value = supertitle_values[0] if len(supertitle_values) > 0 else ''
        jobname_value = jobname_values[0] if len(jobname_values) > 0 else ''

        title_exclude = any(
            [re.match(title_pattern, title_value) for title_pattern in self._compiled_title_regexs]
        )
        supertitle_exclude = any(
            [re.match(supertitle_pattern, supertitle_value) for supertitle_pattern in self._compiled_supertitle_regexs]
        )
        jobname_exclude = any(
            [re.match(jobname_pattern, jobname_value) for jobname_pattern in self._compiled_jobname_regexs]
        )
        return not(title_exclude or supertitle_exclude or jobname_exclude)
