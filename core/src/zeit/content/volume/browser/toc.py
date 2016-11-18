# -*- coding: utf-8 -*-
import StringIO
import csv
import urlparse
import tinydav
import re
import sys
import logging
import lxml.etree
import posixpath
from ordereddict import OrderedDict
from tinydav.exception import HTTPUserError
import zeit.cms.browser.view
from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.connector.connector
import toc_config
import zope.file.download
import zope.app.appsetup.product
import zope.site.site
import zope.component
import zope.component.registry
from zeit.cms.repository.interfaces import IFolder
from zeit.content.article.interfaces import IArticle

log = logging.getLogger(__name__)
# TODO Author/Title Teaser contains is ugly

"""
# This Error occurs if u visit localhost:8080/++skin++vivi/repository/2016/25/
2016-11-18 12:08:00,083 WARNI zeit.cms.content.dav Could not parse DAV property value 'CW1' for Article.page at http://xml.zeit.de/2016/25/Neudeck-box-1 [ValueError: ("invalid literal for int() with base 10: 'CW1'",)]. Using default None instead.
-> Parse Page, differently?


#TODO Nachfragen, ob man die dav archive url immer auf die echten Daten zeigen sollte.
Ich denke schon - Tests kann man ja in testing.py austricksen, oder?

TODO: Nachfragen "Die Product-Config ist leider untypisiert (also nur Strings); an anderen Stellen benutzten wir deshalb Leerzeichen als Trenner."
Ich interpretier das mal so, dass ich das auch in die config packen sollte.

# TODO als letztes
So generell zu dieser Klasse: ich find beim Lesen irgendwie nie die Methode, die ich suche. ;) Als typische Ordnung find ich hilfreich, die "wichtigen" oder "Einstiegspunkte" zuoberst, und dann unterhalb jeder Funktion halt die Hilfsfunktionen, die dort aufgerufen werden -- insbesondere wenn die Hilfsfunktionen vor allem der Gliederung und Benamsung dienen (und nicht unbedingt an verschiedenen Stellen aufgerufen werden).

Vermutlich sind die Datenmengen nicht so riesig, aber Zope kann das View-Ergebnis anstatt als String auch direkt aus nem file-like-object zurückgeben, siehe zope.file.download.DownloadResult.
# TODO
zope.file.download.DownloadResult -> will er nicht weil, StringIO nicht zope-like

Traceback (most recent call last):
  File "/usr/lib/python2.7/unittest/case.py", line 329, in run
    testMethod()
  File "/home/knut/Code/Zeit/vivi-deployment/work/source/zeit.content.volume/src/zeit/content/volume/browser/tests/test_toc.py", line 119, in test_create_csv_with_not_all_values_in_toc_data
    assert toc.CSV_DELIMITER*2 in toc._create_csv(input_data)
  File "/home/knut/Code/Zeit/vivi-deployment/work/source/zeit.content.volume/src/zeit/content/volume/browser/toc.py", line 257, in _create_csv
    file_content = zope.file.download.DownloadResult(out)
  File "/home/knut/Code/Zeit/vivi-deployment/work/_/home/knut/.batou-shared-eggs/zope.file-0.6.2-py2.7.egg/zope/file/download.py", line 76, in __init__
    zope.security.proxy.removeSecurityProxy(context.openDetached()))
AttributeError: StringIO instance has no attribute 'openDetached'

Aber wenn ich so was mache wie
 out = zope.file.file.File()

Also just diese Eigenschaften sind zu dieser Stufe des Print-Imports schon im von vivi erwarteten Format vorhanden,
insofern könnte man überlegen, statt von Hand parsen einen z.c.article.article.Article(xml_file_pointer) zu verwenden.
Also von der Bedienung her wär es schon deutlich bequemer, wenn man zeit.cms.repository.folder.Folder und Co verwenden würde...

connector = zeit.connector.connector.TransactionBoundCachingConnector({'default': 'http://cms-backend:9000/cms/archiv-wf/archiv/'})
cached_resource = connector['http://xml.zeit.de/ZEI/']
cached_resource
folder = ICMSContent(cached_resource)
>>> folder
<zeit.cms.repository.folder.Folder http://xml.zeit.de/ZEI/>
>>> dir(folder)
['__class__', '__contains__', '__delattr__', '__delitem__', '__dict__', '__doc__', '__format__', '__getattribute__', '__getitem__', '__hash__', '__implemented__', '__init__', '__iter__', '__len__', '__module__', '__name__', '__new__', '__parent__', '__providedBy__', '__provides__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setitem__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_get_id_for_name', '_local_unique_map', '_local_unique_map_data', 'connector', 'get', 'has_key', 'items', 'keys', 'repository', 'uniqueId', 'values']
>>> for v in folder.values():
...     v
...

Um das ganze schnell in der Shell zu testen, muss dann noch der alte Connector unregistered werden.
import zeit.connector.connector
connector = zeit.connector.connector.TransactionBoundCachingConnector({'default': 'http://cms-backend:9000/cms/archiv-wf/archiv/'})
import zope.component
zope.component.provideUtility(connector)
import zeit.cms.interfaces
sm = zope.component.getSiteManager()
from zeit.connector.interfaces import IConnector
sm.unregisterUtility(provided=IConnector)
ls -l   zope.component.hooks.setSite(root)

Lösung
Zope Component
Mechanismus zu dependency Injection.
Der Seite Manager:
- schlaues Dict
Kann man verschiedene machen.
Der Default ist, der BaseComponentManager oder so, an bindet man einen neuen anderen.
connector = TransactionBoundConnector(...)

Hole dir zu einem Context den Site-Manager. Das ist eine Registry wo man Utilities und Adapter registrieren kann.
Es gibt einen Globalen Site Manger und den lokalen. Am Anfang hat man per defautl den Global, beim traversieren
kann aber dieser durch einen lokalen ersetzt werden, der dann den globalen ersetzt. Der hat dann vielleicht andere Utilities
und Adapter zur Verfügunge, z.B. wie hier einen anderen Connector.

default_registry = zope.component.getSiteManager()
registry = zope.component.registry.Components(name='toc', bases=(default_registry,))
registry.registerUtility(connector)
site = zope.site.site.SiteManagerContainer()
site.setSiteManager(registry)
zope.component.hooks.setSite(site)

Das führt zu folgendem Traceback im Test
File "/home/knut/Code/Zeit/vivi-deployment/work/source/zeit.content.volume/src/zeit/content/volume/browser/toc.py", line 171, in _create_dav_archive_connector
    registry = zope.component.registry.Components(name='toc', bases=(default_registry,))
  File "/home/knut/Code/Zeit/vivi-deployment/work/_/home/knut/.batou-shared-eggs/zope.component-3.10.0-py2.7.egg/zope/component/registry.py", line 49, in __init__
    self.__bases__ = tuple(bases)
  File "/home/knut/Code/Zeit/vivi-deployment/work/_/home/knut/.batou-shared-eggs/zope.component-3.10.0-py2.7.egg/zope/component/registry.py", line 78, in <lambda>
    lambda self, bases: self._setBases(bases),
  File "/home/knut/Code/Zeit/vivi-deployment/work/_/home/knut/.batou-shared-eggs/zope.component-3.10.0-py2.7.egg/zope/component/registry.py", line 71, in _setBases
    base.adapters for base in bases])
  File "/home/knut/Code/Zeit/vivi-deployment/work/_/home/knut/.batou-shared-eggs/zope.interface-4.0.5-py2.7-linux-x86_64.egg/zope/interface/adapter.py", line 90, in <lambda>
    lambda self, bases: self._setBases(bases),
  File "/home/knut/Code/Zeit/vivi-deployment/work/_/home/knut/.batou-shared-eggs/zope.interface-4.0.5-py2.7-linux-x86_64.egg/zope/interface/adapter.py", line 638, in _setBases
    r._addSubregistry(self)
AttributeError: '_LocalAdapterRegistry' object has no attribute '_addSubregistry'


Man muss sich hier nicht mehr kümmern, was dann passiert.


Das habe ich noch nicht so gut verstanden!
Idee von Site Object. An der Site hängt die registry.
Beim traversieren über eine Site object wird dann wird zope.component.hooks.setSite(site) gemacht.
    ------
2016-11-14T15:01:41 WARNING zeit.cms.content.dav Could not parse DAV property value '65-65' for Article.page at http://xml.zeit.de/ZEI/2016/23/chancen/C-Frauen-Karriere [ValueError: ("invalid literal for int() with base 10: '65-65'",)]. Using default None instead.

Da die XML's doch hier noch nicht so schön ist, also doch parsen.
Es sollte durch einen Kommentar klar werden, dass

Tests
Umstellung auf neue Implementation
Config-Kram für die Product IDs
Kommentieren
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
        config = zope.app.appsetup.product.getProductConfiguration('zeit.content.volume')
        self.dav_archive_url = config.get('dav-archive-url')
        self.dav_archive_url_parsed = self._parse_config()
        self.client = self._create_dav_client()
        self.excluder = Excluder()
        self.connector = None

    def _parse_config(self):
        """
        Parse DAV-Archive URL.
        :return: urlparse.ParseResult
        """
        return urlparse.urlparse(self.dav_archive_url)

    def __call__(self):
        self.connector = self._create_dav_archive_connector()
        self.product_id_mapping = self._create_product_id_full_name_mapping()
        filename = self._generate_file_name()
        self.request.response.setHeader('Content-Type', 'text/csv')
        self.request.response.setHeader(
            'Content-Disposition', 'attachment; filename="%s"' % filename)
        return self._create_toc_content()

    def _create_dav_archive_connector(self):
        # A new registry has to be provided to register the
        # toc specific connector
        # default_registry = zope.component.getSiteManager()
        # registry = zope.component.registry.Components(name='toc', bases=(default_registry,))
        # registry.registerUtility(connector)
        # site = zope.site.site.SiteManagerContainer()
        # site.setSiteManager(registry)
        # zope.component.hooks.setSite(site)
        # default_registry = zope.component.getSiteManager()
        # site = zope.site.site.SiteManagerContainer()
        # site.__parent__ = default_registry.__parent__
        # registry = zope.site.site.LocalSiteManager(site, default_folder=False)
        # site.setSiteManager(registry)
        # registry.registerUtility(connector)
        # zope.component.hooks.setSite(site)
        # This should be non-persistent
        default_registry = zope.component.getSiteManager()
        site = zope.site.site.SiteManagerContainer()
        registry = zope.site.site.LocalSiteManager(site, default_folder=False)
        registry.__bases__ =  (default_registry,)
        site.setSiteManager(registry)
        connector = zeit.connector.connector.TransactionBoundCachingConnector(
             {'default': self.dav_archive_url})
        registry.registerUtility(connector)
        zope.component.hooks.setSite(site)
        return connector


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
            #for ressort_path in self.list_relevant_ressort_dirs_with_dav(product_path):
            for ressort_folder_name, ressort_folder in self.list_relevant_ressort_folders_with_archive_connector(product_path):
                import pdb; pdb.set_trace()
                result_for_ressort = []
                # for article_path in self._get_all_articles_in_path(ressort_path):
                # import pdb; pdb.set_trace()
                # Her
                for article_path in self._get_all_articles_in_folder(ressort_folder):
                    import pdb; pdb.set_trace()
                    toc_entry = self._create_toc_element(article_path)
                    if toc_entry:
                        result_for_ressort.append(toc_entry)
                result_for_product[ressort_folder_name] = result_for_ressort
            results[self._full_product_name(product_path)] = result_for_product
        return results

    def _get_all_articles_in_folder(self, path):
        """
        Get all DAV Server paths to article files in path.
        :param path: str - archive path to ressort, e.g. 'cms/archiv/ws-archiv/ZEI/2016/23/'
        :return: [str]
        """
        return [resource.xml for _, resource in path.items() if IArticle.providedBy(resource)]
        # all_article_paths = []
        # for article_path in self._get_all_files_in_folder(path):
        #     all_article_paths.append(article_path)
        # return all_article_paths

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
        # This should work for Connector
        # You need the XML prefix here
        prefix = 'http://xml.zeit.de'
        return [posixpath.join(*[str(e) for e in [prefix, dir_name, self.context.year, volume_string, '']])
            for dir_name in product_dir_names]
        # return [posixpath.join(*[str(e) for e in [self.dav_archive_url_parsed.path, dir_name, self.context.year, volume_string, '']])
        #         for dir_name in product_dir_names]

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
        return self.excluder.is_relevant(article_tree)

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

    def list_relevant_ressort_folders_with_archive_connector(self, path):
        try:
            product_folder = zeit.cms.interfaces.ICMSContent(self.connector[path])
            return [item for item in product_folder.items() if self._is_relevant_folder_item(item)]
        except KeyError:
            return []

    def _is_relevant_folder_item(self, item):
        # item ('name', adapted DAV-Resource?)
        return self.excluder.is_relevant_folder(item[0]) and IFolder.providedBy(item[1])

    def _is_relevant_path_to_directory(self, root_path_of_element, element):
        """

        :param root_path_of_element: root path oyf DAV archive
        :param element: tinydav status element
        :return: bool
        """
        try:
            root_paths = {root_path_of_element, '/' + root_path_of_element}
            return self._is_dav_dir(element) \
                   and not self.excluder.is_relevant_folder(element.href) \
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
        # import transaction
        # from zope.file.download import DownloadResult
        # from zope.file.file import File
        # out = File()
        # w = out.open('w')
        # writer = csv.writer(w, delimiter=self.CSV_DELIMITER)
        # for toc_element in self._generate_csv_rows(toc_data):
        #     writer.writerow(
        #         [val.encode('utf-8') for val in toc_element]
        #     )
        #     transaction.commit()
        #
        # w.flush()
        # w.close()
        # transaction.commit()
        # return DownloadResult(out)

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
        return self._get_metadata_from_article_xml(doc_path) \
            if self._is_relevant_article(doc_path) else None

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


class Excluder(object):
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

    def is_relevant_folder(self, folder_path):
        folders_to_exclude = {'images', 'leserbriefe'}
        folders_to_exclude = set.union(folders_to_exclude, {ele.title() for ele in folders_to_exclude})
        return not any(folder in folder_path for folder in folders_to_exclude)


