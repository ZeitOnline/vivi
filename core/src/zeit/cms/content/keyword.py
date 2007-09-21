# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import urllib2
import weakref

import rwproperty

import zope.interface

import gocept.lxml.objectify

import zeit.cms.config
import zeit.cms.browser.tree
import zeit.cms.content.interfaces


class Keyword(object):

    zope.interface.implements(zeit.cms.content.interfaces.IKeyword)

    def __init__(self, code, label):
        self.code = unicode(code)
        self.label = unicode(label)
        self._broader = None
        self.narrower = []

    @rwproperty.getproperty
    def broader(self):
        if self._broader is None:
            return None
        return self._broader()

    @rwproperty.setproperty
    def broader(self, value):
        self._broader = weakref.ref(value)


@gocept.cache.method.Memoize(3600)
def keyword_root_factory():

    def pcv(node_name):
        pcv_ns = 'http://prismstandard.org/namespaces/1.2/pcv/'
        return '{%s}%s' % (pcv_ns, node_name)

    def rdf(node_name):
        rdf_ns = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
        return '{%s}%s' % (rdf_ns, node_name)

    request = urllib2.urlopen(zeit.cms.config.KEYWORD_URL)
    prism_tree = gocept.lxml.objectify.fromfile(request)
    keywords = {}
    descriptors = []
    root_keyword = None

    # Iteration 1: Create keywords
    for descriptor in prism_tree[pcv('Descriptor')][:]:
        code = descriptor[pcv('code')]
        label = descriptor[pcv('label')]
        rdf_id = descriptor.get(rdf('ID'))
        keywords[rdf_id] = Keyword(code, label)
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

    return root_keyword


class KeywordTree(zeit.cms.browser.tree.Tree):

    key = 'zeit.cms.content.keyword'

    @property
    def root(self):
        pass

    def isRoot(self, container):
        pass

    def getUniqueId(self, object):
        raise NotImplementedError

    def selected(self, url):
        raise NotImplementedError


