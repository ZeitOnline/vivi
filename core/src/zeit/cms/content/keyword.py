# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import logging
import urllib2
import weakref

import rwproperty

import zope.interface
import zope.app.appsetup.product

import gocept.lxml.objectify

import zeit.cms.content.interfaces
import zeit.cms.content.property


logger = logging.getLogger(__name__)


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
    _loaded = False

    @zope.cachedescriptors.property.readproperty
    def root(self):
        self._load_keywords()
        return self.root

    def __contains__(self, code):
        self._load_keywords()
        return code in self._keywords_by_code

    def __getitem__(self, code):
        self._load_keywords()
        return self._keywords_by_code[code]

    def find_keywords(self, searchterm):
        self._load_keywords()
        return (
            self[x] for x in self._keywords_by_code.keys()
            if searchterm.lower() in x.lower())

    def _load_keywords(self):
        if self._loaded:
            return

        def pcv(node_name):
            pcv_ns = 'http://prismstandard.org/namespaces/1.2/pcv/'
            return '{%s}%s' % (pcv_ns, node_name)

        def rdf(node_name):
            rdf_ns = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
            return '{%s}%s' % (rdf_ns, node_name)

        cms_config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.cms')
        url = cms_config['source-keyword']
        logger.info('Loading keywords from %s' % url)
        request = urllib2.urlopen(url)
        prism_tree = gocept.lxml.objectify.fromfile(request)
        keywords = {}
        descriptors = []
        root_keyword = None
        self._keywords_by_code = {}

        # Iteration 1: Create keywords
        for descriptor in prism_tree[pcv('Descriptor')][:]:
            code = descriptor[pcv('code')]
            label = descriptor[pcv('label')]
            rdf_id = descriptor.get(rdf('ID'))

            keyword = Keyword(code, label, True)
            keywords[rdf_id] = keyword
            self._keywords_by_code[unicode(code)] = keyword

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

        self.root = root_keyword
        self._loaded = True


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
        logger.warning("Ignored keyword %s, not in taxonomy." % rdf_id)
        return None

    def _node_factory(self, entry, tree):
        return entry.code
