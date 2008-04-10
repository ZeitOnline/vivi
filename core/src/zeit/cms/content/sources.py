# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import logging
import operator
import urllib2
import xml.sax.saxutils

import zope.component
import zope.app.appsetup.product

import zc.sourcefactory.basic
import zc.sourcefactory.contextual
import gocept.lxml.objectify
import gocept.cache.method

import zeit.cms.interfaces


logger = logging.getLogger('zeit.cms.content.sources')


class SimpleXMLSourceBase(object):

    product_configuration = 'zeit.cms'

    @gocept.cache.method.Memoize(60)
    def _get_tree(self):
        cms_config = zope.app.appsetup.product.getProductConfiguration(
            self.product_configuration)
        url = cms_config[self.config_url]
        return self._get_tree_from_url(url)

    @gocept.cache.method.Memoize(3600, ignore_self=True)
    def _get_tree_from_url(self, url):
        __traceback_info__ = (url, )
        logger.debug('Getting %s' % url)
        request = urllib2.urlopen(url)
        return gocept.lxml.objectify.fromfile(request)

    @gocept.cache.method.Memoize(60)
    def getValues(self):
        xml = self._get_tree()
        return [unicode(serie).strip() for serie in xml.iterchildren()]


class SimpleXMLSource(
    SimpleXMLSourceBase,
    zc.sourcefactory.basic.BasicSourceFactory):
    """A simple xml source."""


class SimpleContextualXMLSource(
    SimpleXMLSourceBase,
    zc.sourcefactory.contextual.BasicContextualSourceFactory):
    """a simple contextual xml source."""

    def getValues(self, context):
        return super(SimpleContextualXMLSource, self).getValues()


class PrintRessortSource(SimpleXMLSource):

    config_url = 'source-print-ressort'


class NavigationSource(SimpleXMLSource):

    config_url = 'source-navigation'

    @gocept.cache.method.Memoize(60)
    def getValues(self):
        tree = self._get_tree()
        return [unicode(ressort.get('name'))
                for ressort in tree.iterchildren()]

    @gocept.cache.method.Memoize(60)
    def getTitle(self, value):
        __traceback_info__ = (value, )
        tree = self._get_tree()
        return unicode(tree.xpath('/ressorts/ressort[@name = "%s"]' %
                                  value)[0]['title'])


class SerieSource(SimpleXMLSource):

    config_url = 'source-serie'


class SubNavigationSource(SimpleContextualXMLSource):
    """Source for the subnavigation."""

    config_url = 'source-navigation'

    def getValues(self, context):
        ressort_nodes = self._get_ressort_nodes(context)
        sub_navs = reduce(
            operator.add, [ressort_node.findall('subnavigation')
             for ressort_node in ressort_nodes])
        return [unicode(sub.get('name'))
                for sub in sub_navs]

    @gocept.cache.method.Memoize(60)
    def getTitle(self, context, value):
        tree = self._get_tree()
        nodes = tree.xpath('//subnavigation[@name = "%s"]' % value)
        assert len(nodes) == 1
        return unicode(nodes[0]['title'])

    def _get_ressort_nodes(self, context):
        tree = self._get_tree()
        all_ressorts = tree.ressort
        metadata = zeit.cms.content.interfaces.ICommonMetadata(context, None)
        if metadata is None:
            return all_ressorts
        ressort = metadata.ressort
        if not ressort:
            return all_ressorts

        nodes = tree.xpath(
            '/ressorts/ressort[@name = %s]' %
            xml.sax.saxutils.quoteattr(ressort))
        if not nodes:
            return None
        assert len(nodes) == 1
        return nodes


class CMSContentTypeSource(zc.sourcefactory.basic.BasicSourceFactory):

    def getValues(self):
        return (interface for name, interface in
                zope.component.getUtilitiesFor(
                    zeit.cms.interfaces.ICMSContentType))


_collect_counter = 0
@zope.component.adapter(zope.app.publication.interfaces.IBeforeTraverseEvent)
def collect_caches(event):
    """Collect method cache every 100 requests.

    Don't collect on every request because collect is O(n**2) in regard to the
    number of cached methods/functions and the amount of cached values.

    """
    global _collect_counter
    _collect_counter += 1
    if _collect_counter >= 100:
        logger.debug("Collecting caches.")
        # collect every 100 requests
        gocept.cache.method.collect()
        _collect_counter = 0
