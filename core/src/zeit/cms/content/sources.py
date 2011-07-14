# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import gocept.cache.method
import gocept.lxml.objectify
import logging
import operator
import threading
import urllib2
import xml.sax.saxutils
import zc.sourcefactory.basic
import zc.sourcefactory.contextual
import zeit.cms.interfaces
import zeit.cms.type
import zope.app.appsetup.product
import zope.app.publication.interfaces
import zope.component
import zope.security.proxy
import zope.testing.cleanup


logger = logging.getLogger('zeit.cms.content.sources')


class SimpleXMLSourceBase(object):

    product_configuration = 'zeit.cms'
    config_url = NotImplemented

    def _get_tree(self):
        cms_config = zope.app.appsetup.product.getProductConfiguration(
            self.product_configuration)
        url = cms_config[self.config_url]
        return self._get_tree_from_url(url)

    @gocept.cache.method.Memoize(600, ignore_self=True)
    def _get_tree_from_url(self, url):
        __traceback_info__ = (url, )
        logger.debug('Getting %s' % url)
        request = urllib2.urlopen(url)
        return gocept.lxml.objectify.fromfile(request)

    def getValues(self):
        xml = self._get_tree()
        return [unicode(serie).strip() for serie in xml.iterchildren()]


class XMLSource(
    SimpleXMLSourceBase,
    zc.sourcefactory.contextual.BasicContextualSourceFactory):
    # NOTE: this source is contextual to be able to set a default for a field
    # using the source even while there is no product config.

    attribute = NotImplemented

    def getValues(self, context):
        tree = self._get_tree()
        return [unicode(node.get(self.attribute))
                for node in tree.iterchildren()]

    def getTitle(self, context, value):
        __traceback_info__ = (value, )
        tree = self._get_tree()
        nodes = tree.xpath('//*[@%s= %s]' % (
                           self.attribute,
                           xml.sax.saxutils.quoteattr(value)))
        if nodes:
            return unicode(nodes[0].text).strip()
        return value


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


class SimpleFixedValueSource(zc.sourcefactory.basic.BasicSourceFactory):

    values = NotImplemented

    def __init__(self):
        self.titles = dict((x, _(x)) for x in self.values)

    def getValues(self):
        return self.values

    def getTitle(self, value):
        return self.titles.get(value, value)


class PrintRessortSource(SimpleXMLSource):

    config_url = 'source-print-ressort'


class NavigationSource(SimpleXMLSource):

    config_url = 'source-navigation'

    def getValues(self):
        tree = self._get_tree()
        return [unicode(ressort.get('name'))
                for ressort in tree.iterchildren()]

    def getTitle(self, value):
        __traceback_info__ = (value, )
        tree = self._get_tree()
        nodes = tree.xpath('/ressorts/ressort[@name = %s]' %
                           xml.sax.saxutils.quoteattr(value))
        if nodes:
            return unicode(nodes[0]['title'])
        return value


class SerieSource(SimpleXMLSource):

    config_url = 'source-serie'


class SubNavigationSource(SimpleContextualXMLSource):
    """Source for the subnavigation."""

    config_url = 'source-navigation'

    def getValues(self, context):
        __traceback_info__ = (context,)
        ressort_nodes = self._get_ressort_nodes(context)
        sub_navs = reduce(
            operator.add, [ressort_node.findall('subnavigation')
             for ressort_node in ressort_nodes])
        result = set([unicode(sub.get('name'))
                    for sub in sub_navs])
        return result

    def getTitle(self, context, value):
        tree = self._get_tree()
        ressort = self._get_ressort(context)
        if ressort is None:
            nodes = tree.xpath(
                '//subnavigation[@name = %s]' % (
                    xml.sax.saxutils.quoteattr(value)))
        else:
            nodes = tree.xpath(
                '/ressorts/ressort[@name = %s]/subnavigation[@name = %s]' % (
                    xml.sax.saxutils.quoteattr(ressort),
                    xml.sax.saxutils.quoteattr(value)))
        if nodes:
            return unicode(nodes[0]['title'])
        return value

    def _get_ressort_nodes(self, context):
        tree = self._get_tree()
        all_ressorts = tree.ressort
        ressort = self._get_ressort(context)
        if not ressort:
            return all_ressorts

        nodes = tree.xpath('/ressorts/ressort[@name = "%s"]' % ressort)
        if not nodes:
            return None
        assert len(nodes) == 1
        return nodes

    def _get_ressort(self, context):
        if isinstance(context, unicode):
            return context
        if zeit.cms.interfaces.ICMSContent.providedBy(context):
            return None
        metadata = zeit.cms.content.interfaces.ICommonMetadata(context, None)
        if metadata is None:
            return None
        return metadata.ressort


class Product(object):

    def __init__(self, id=None, title=None, vgwortid=None):
        self.id = id
        self.title = title
        self.vgwortid = vgwortid

    def __eq__(self, other):
        if not zope.security.proxy.isinstance(other, self.__class__):
            return False
        return self.id == other.id


def int_or_none(value):
    try:
        return int(value)
    except TypeError:
        return None


class ProductSource(
    SimpleXMLSourceBase,
    zc.sourcefactory.contextual.BasicContextualSourceFactory):

    config_url = 'source-products'

    def getValues(self, context):
        tree = self._get_tree()
        return [Product(unicode(node.get('id')),
                        unicode(node.text.strip()),
                        int_or_none(node.get('vgwortid')))
                for node in tree.iterchildren()]

    def getTitle(self, context, value):
        return value.title

    def getToken(self, context, value):
        return super(ProductSource, self).getToken(context, value.id)


class CMSContentTypeSource(zc.sourcefactory.basic.BasicSourceFactory):

    def getValues(self):
        return (interface for name, interface in
                zope.component.getUtilitiesFor(
                    zeit.cms.interfaces.ICMSContentType))

    def getTitle(self, value):
        try:
            return value.getTaggedValue('zeit.cms.title')
        except KeyError:
            return unicode(value)


class AddableCMSContentTypeSource(CMSContentTypeSource):

    def filterValue(self, value):
        return (value.queryTaggedValue('zeit.cms.addform') !=
                zeit.cms.type.SKIP_ADD)


_collect_lock = threading.Lock()
_collect_counter = 0
@zope.component.adapter(zope.app.publication.interfaces.IBeforeTraverseEvent)
def collect_caches(event):
    """Collect method cache every 100 requests.

    Don't collect on every request because collect is O(n**2) in regard to the
    number of cached methods/functions and the amount of cached values.

    """
    global _collect_counter
    _collect_counter += 1
    if _collect_counter < 100:
        return
    locked = _collect_lock.acquire(False)
    if not locked:
        return
    try:
        logger.debug("Collecting caches.")
        # collect every 100 requests
        gocept.cache.method.collect()
        _collect_counter = 0
    finally:
        _collect_lock.release()


zope.testing.cleanup.addCleanUp(gocept.cache.method.clear)
