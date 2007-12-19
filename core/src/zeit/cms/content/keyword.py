# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import urllib2
import weakref

import rwproperty

import zope.interface
import zope.app.appsetup.product

import gocept.lxml.objectify

import zeit.cms.content.interfaces


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

    def __getitem__(self, code):
        self._load_keywords()
        try:
            return self._keywords_by_code[code]
        except KeyError:
            return Keyword(code, code, in_taxonomy=False)

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
        request = urllib2.urlopen(cms_config['source-keyword'])
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
