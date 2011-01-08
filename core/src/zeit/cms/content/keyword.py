# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import logging
import lxml.objectify
import pytz
import rwproperty
import threading
import urllib2
import weakref
import zope.app.appsetup.product
import zope.interface

import zeit.cms.content.interfaces
import zeit.cms.content.property


log = logging.getLogger(__name__)


class Keyword(object):

    zope.interface.implements(zeit.cms.content.interfaces.IKeyword)

    def __init__(self, code, label, in_taxonomy=False):
        self.code = unicode(code)
        self.label = unicode(label)
        self._broader = None
        self.narrower = []
        self.inTaxonomy = in_taxonomy

    @rwproperty.getproperty
    def broader(self):
        if self._broader is None:
            return None
        return self._broader()

    @rwproperty.setproperty
    def broader(self, value):
        self._broader = weakref.ref(value)


class KeywordUtility(object):

    zope.interface.implements(zeit.cms.content.interfaces.IKeywords)
    reload_interval = datetime.timedelta(seconds=360)
    loaded = None
    load_lock = threading.Lock()

    @property
    def root(self):
        self._load_keywords()
        return self._root

    def __contains__(self, code):
        self._load_keywords()
        return code in self._keywords_by_code

    def __getitem__(self, code):
        self._load_keywords()
        return self._keywords_by_code[code]

    def find_keywords(self, searchterm):
        self._load_keywords()
        searchterm = searchterm.lower()
        return (
            keyword for code, keyword in self._keywords_by_code.items()
            if (searchterm in code.lower()
                or searchterm in keyword.label.lower()))

    def _load_keywords(self):
        if self.loaded is None:
            self.load_lock.acquire()
        else:
            locked = False
            if self.loaded + self.reload_interval < datetime.datetime.now(
                pytz.UTC):
                locked = self.load_lock.acquire(False)
            if not locked:
                return
        try:

            def pcv(node_name):
                pcv_ns = 'http://prismstandard.org/namespaces/1.2/pcv/'
                return '{%s}%s' % (pcv_ns, node_name)

            def rdf(node_name):
                rdf_ns = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
                return '{%s}%s' % (rdf_ns, node_name)

            prism_tree = self.load_tree()

            keywords = {}
            descriptors = []
            root_keyword = None
            keywords_by_code = {}

            # Iteration 1: Create keywords
            for descriptor in prism_tree[pcv('Descriptor')][:]:
                code = descriptor[pcv('code')]
                label = descriptor[pcv('label')]
                rdf_id = descriptor.get(rdf('ID'))

                keyword = Keyword(code, label, True)
                keywords[rdf_id] = keyword
                keywords_by_code[unicode(code)] = keyword

                descriptors.append((rdf_id, descriptor))

            # Iteration 2: Connect keywords
            for rdf_id, descriptor in descriptors:
                keyword = keywords[rdf_id]
                try:
                    narrower_terms = descriptor[pcv('narrowerTerm')][:]
                except AttributeError:
                    pass
                else:
                    for narrower in narrower_terms:
                        narrower_id = narrower.get(rdf('resource'))
                        keyword.narrower.append(keywords[narrower_id])
                try:
                    broader = descriptor[pcv('broaderTerm')]
                except AttributeError:
                    if root_keyword is not None:
                        raise ValueError("Found multiple root keywords.")
                    root_keyword = keyword
                else:
                    broader_id = broader.get(rdf('resource'))
                    keyword.broader = keywords[broader_id]

            self._root = root_keyword
            self._keywords_by_code = keywords_by_code
            self.loaded = datetime.datetime.now(pytz.UTC)
        except:
            log.error('Could not load keywords.', exc_info=True)
        finally:
            self.load_lock.release()

    def load_tree(self):
        cms_config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.cms')
        url = cms_config['source-keyword']
        log.info('Loading keywords from %s' % url)
        request = urllib2.urlopen(url)
        return lxml.objectify.parse(request).getroot()


class KeywordsProperty(zeit.cms.content.property.MultiPropertyBase):

    def __init__(self):
        super(KeywordsProperty, self).__init__('.head.keywordset.keyword')

    def __set__(self, instance, value):
        super(KeywordsProperty, self).__set__(instance, value)
        tree = instance.xml
        for keyword in self.path.find(tree, []):
            keyword.set('source', 'manual')

    def _element_factory(self, node, tree):
        taxonomy = zope.component.getUtility(
            zeit.cms.content.interfaces.IKeywords)
        rdf_id = unicode(node)
        if rdf_id in taxonomy:
            return taxonomy[rdf_id]
        log.warning("Ignored keyword %s, not in taxonomy." % rdf_id)
        return None

    def _node_factory(self, entry, tree):
        return entry.code
