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
import zope.app.appsetup.product
import zope.app.publication.interfaces
import zope.component
import zope.dottedname
import zope.i18n
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
        return [unicode(serie).strip() for serie in xml.iterchildren('*')]


class XMLSource(
    SimpleXMLSourceBase,
    zc.sourcefactory.contextual.BasicContextualSourceFactory):
    # NOTE: this source is contextual to be able to set a default for a field
    # using the source even while there is no product config.

    attribute = NotImplemented
    title_xpath = '//*'

    def getValues(self, context):
        tree = self._get_tree()
        return [unicode(node.get(self.attribute))
                for node in tree.iterchildren('*')
                if self.isAvailable(node, context)]

    def isAvailable(self, node, context):
        # NOTE: the *default* value must not use ``available``, since e.g.
        # newly created objects do not have their marker interfaces yet when
        # they are assigned the default value, which would lead to
        # ConstraintNotSatisfied errors.
        iface = node.get('available', 'zope.interface.Interface')
        try:
            iface = zope.dottedname.resolve.resolve(iface)
        except ImportError:
            return False
        return iface.providedBy(context)

    def getTitle(self, context, value):
        __traceback_info__ = (value, )
        tree = self._get_tree()
        nodes = tree.xpath('%s[@%s= %s]' % (
                           self.title_xpath,
                           self.attribute,
                           xml.sax.saxutils.quoteattr(value)))
        if nodes:
            return self._get_title_for(nodes[0])
        return value

    def _get_title_for(self, node):
        return unicode(node.text).strip()


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


class NavigationSource(XMLSource):

    config_url = 'source-navigation'
    attribute = 'name'
    title_xpath = '/ressorts/ressort'

    def _get_title_for(self, node):
        return unicode(node['title'])


class MasterSlaveSource(XMLSource):

    slave_tag = NotImplemented
    master_node_xpath = NotImplemented
    master_value_iface = NotImplemented
    master_value_key = NotImplemented

    def getValues(self, context):
        __traceback_info__ = (context,)
        master_nodes = self._get_master_nodes(context)
        slave_nodes = reduce(
            operator.add, [
                node.findall(self.slave_tag) for node in master_nodes])
        result = set([unicode(node.get(self.attribute)) for node in slave_nodes
                      if self.isAvailable(node, context)])
        return result

    def getTitle(self, context, value):
        tree = self._get_tree()
        master_value = self._get_master_value(context)
        if master_value is None:
            nodes = tree.xpath(
                '//%s[@%s = %s]' % (
                    self.slave_tag, self.attribute,
                    xml.sax.saxutils.quoteattr(value)))
        else:
            nodes = tree.xpath(
                '{master_node_xpath}[@{attribute} = {master}]'
                '/{slave_tag}[@{attribute} = {slave}]'.format(
                    master_node_xpath=self.master_node_xpath,
                    attribute=self.attribute,
                    slave_tag=self.slave_tag,
                    master=xml.sax.saxutils.quoteattr(master_value),
                    slave=xml.sax.saxutils.quoteattr(value)))
        if nodes:
            return unicode(self._get_title_for(nodes[0]))
        return value

    def _get_master_nodes(self, context):
        tree = self._get_tree()
        all_nodes = tree.xpath(self.master_node_xpath)
        master_value = self._get_master_value(context)
        if not master_value:
            return all_nodes

        nodes = tree.xpath(
            '{master_node_xpath}[@{attribute} = "{value}"]'.format(
                master_node_xpath=self.master_node_xpath,
                attribute=self.attribute,
                # XXX not sure why we do manual quoting instead of quoteattr
                # here, doesn't feel as it was thought through. There's a
                # random doctest example about 'Bildung & Beruf' however that
                # breaks if I change it.
                value=master_value))
        if not nodes:
            return None
        assert len(nodes) == 1
        return nodes

    def _get_master_value(self, context):
        if isinstance(context, unicode):
            return context
        if zeit.cms.interfaces.ICMSContent.providedBy(context):
            return None
        data = self.master_value_iface(context, None)
        if data is None:
            return None
        return getattr(data, self.master_value_key)


class SubNavigationSource(MasterSlaveSource):

    config_url = 'source-navigation'
    attribute = 'name'
    slave_tag = 'subnavigation'
    master_node_xpath = '/ressorts/ressort'
    master_value_key = 'ressort'

    @property
    def master_value_iface(self):
        # prevent circular import
        import zeit.cms.content.interfaces
        return zeit.cms.content.interfaces.ICommonMetadata

    def _get_title_for(self, node):
        return unicode(node['title'])


class SubChannelSource(SubNavigationSource):

    def _get_master_nodes(self, context):
        if type(context).__name__ == 'Fake':
            # for .browser.MasterSlaveDropdownUpdater
            return super(SubChannelSource, self)._get_master_nodes(context)
        # The ``channels`` field is a list of combination values.
        # The formlib validation machinery does not give us enough context
        # to determine the master value, so we are forced to allow all values.
        # We can get away with this since the UI only offers valid subchannel
        # values (powered by MasterSlaveDropdownUpdater above).
        tree = self._get_tree()
        all_nodes = tree.xpath(self.master_node_xpath)
        return all_nodes


class SerieSource(SimpleContextualXMLSource):

    config_url = 'source-serie'


class Product(object):

    def __init__(self, id=None, title=None, vgwortcode=None,
        href=None, target=None, label=None, show=None):
        self.id = id
        self.title = title
        self.vgwortcode = vgwortcode
        self.href = href
        self.target = target
        self.label = label
        self.show = show

    def __eq__(self, other):
        if not zope.security.proxy.isinstance(other, self.__class__):
            return False
        return self.id == other.id


def unicode_or_none(value):
    if value:
        return unicode(value)


class ProductSource(SimpleContextualXMLSource):

    config_url = 'source-products'

    def getValues(self, context):
        tree = self._get_tree()
        return [Product(unicode(node.get('id')),
                        unicode(node.text.strip()),
                        unicode_or_none(node.get('vgwortcode')),
                        unicode_or_none(node.get('href')),
                        unicode_or_none(node.get('target')),
                        unicode_or_none(node.get('label')),
                        unicode_or_none(node.get('show')))
                for node in tree.iterchildren('*')]

    def getTitle(self, context, value):
        return value.title

    def getToken(self, context, value):
        return super(ProductSource, self).getToken(context, value.id)


class BannerSource(SimpleXMLSource):

    config_url = 'source-banners'

    def getValues(self):
        tree = self._get_tree()
        return [int(node.get('paragraph'))
                for node in tree.xpath('//homepage/page_all')]


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

    def getValues(self):
        import zeit.cms.content.interfaces  # break circular import
        types = (list(super(AddableCMSContentTypeSource, self).getValues())
                 + list(interface for name, interface in
                        zope.component.getUtilitiesFor(
                            zeit.cms.content.interfaces.IAddableContent)))
        by_title = {
            # XXX Hard-code language, since we don't have a request here.
            zope.i18n.translate(self.getTitle(x), target_language='de'): x
            for x in types}
        return [by_title[x] for x in sorted(by_title.keys())]

    def filterValue(self, value):
        import zeit.cms.type  # break circular import
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
