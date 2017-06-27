from zeit.cms.application import CONFIG_CACHE
from zeit.cms.i18n import MessageFactory as _
import collections
import gocept.lxml.objectify
import logging
import operator
import pyramid_dogpile_cache2
import urllib2
import xml.sax.saxutils
import zc.sourcefactory.basic
import zc.sourcefactory.contextual
import zeit.cms.interfaces
import zope.app.appsetup.product
import zope.component
import zope.dottedname
import zope.i18n
import zope.security.proxy
import zope.testing.cleanup


logger = logging.getLogger('zeit.cms.content.sources')
zope.testing.cleanup.addCleanUp(pyramid_dogpile_cache2.clear)


class SimpleXMLSourceBase(object):

    product_configuration = 'zeit.cms'
    config_url = NotImplemented

    def _get_tree(self):
        cms_config = zope.app.appsetup.product.getProductConfiguration(
            self.product_configuration)
        url = cms_config[self.config_url]
        return self._get_tree_from_url(url)

    @CONFIG_CACHE.cache_on_arguments()
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
    """This source should be used in most cases."""
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
    """A simple contextual xml source."""

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


class IObjectSource(zope.schema.interfaces.IIterableSource):
    pass


class ObjectSource(object):

    class source_class(zc.sourcefactory.source.FactoredContextualSource):

        zope.interface.implements(IObjectSource)

        def find(self, id):
            return self.factory.find(self.context, id)

    def _values(self):
        raise NotImplementedError()

    def getTitle(self, context, value):
        return value.title

    def getToken(self, context, value):
        return value.id

    def isAvailable(self, value, context):
        return value.is_allowed(context)

    def getValues(self, context):
        return [x for x in self._values().values()
                if self.isAvailable(x, context)]

    def find(self, context, id):
        value = self._values().get(id)
        if (not value or not self.isAvailable(value, context) or
                not self.filterValue(context, value)):
            return None
        return value


class AllowedBase(object):

    def __init__(self, id, title, available):
        self.id = id
        self.title = title

        if available is None:
            available = 'zope.interface.Interface'
        try:
            available = zope.dottedname.resolve.resolve(available)
        except ImportError:
            available = None
        self.available_iface = available

    def is_allowed(self, context):
        if self.available_iface is None:
            return False
        return self.available_iface.providedBy(context)

    def __eq__(self, other):
        return zope.security.proxy.isinstance(
            other, self.__class__) and self.id == other.id


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
                '//{slave_tag}[@{attribute} = {value}]'.format(
                    slave_tag=self.slave_tag,
                    attribute=self.attribute,
                    value=xml.sax.saxutils.quoteattr(value)))
        else:
            nodes = tree.xpath(
                '{master_node_xpath}[@{attribute} = {master}]'
                '/{slave_tag}[@{attribute} = {value}]'.format(
                    master_node_xpath=self.master_node_xpath,
                    attribute=self.attribute,
                    slave_tag=self.slave_tag,
                    master=xml.sax.saxutils.quoteattr(master_value),
                    value=xml.sax.saxutils.quoteattr(value)))
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


class ChannelSource(XMLSource):

    config_url = 'source-channels'
    attribute = 'name'
    title_xpath = '/ressorts/ressort'

    def _get_title_for(self, node):
        return unicode(node['title'])


class SubChannelSource(MasterSlaveSource):

    config_url = ChannelSource.config_url
    attribute = ChannelSource.attribute
    slave_tag = 'subnavigation'
    master_node_xpath = '/ressorts/ressort'
    master_value_key = 'ressort'

    @property
    def master_value_iface(self):
        # prevent circular import
        import zeit.cms.content.interfaces
        return zeit.cms.content.interfaces.ICommonMetadata

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

    def _get_title_for(self, node):
        return unicode(node['title'])


def unicode_or_none(value):
    if value:
        return unicode(value)


class Serie(object):

    def __init__(self, serienname=None, title=None, url=None, encoded=None,
                 column=False, video=False):
        self.serienname = serienname
        self.title = title
        self.url = url
        self.encoded = encoded
        self.column = column
        self.video = video

    def __eq__(self, other):
        if not zope.security.proxy.isinstance(other, self.__class__):
            return False
        return self.serienname == other.serienname


class SerieSource(SimpleContextualXMLSource):

    config_url = 'source-serie'

    @property
    def values(self):
        return self._fill_values()

    @CONFIG_CACHE.cache_on_arguments()
    def _fill_values(self):
        result = collections.OrderedDict()
        for node in self._get_tree().iterchildren('*'):
            # XXX: For compat reasons we need a fallback `serienname`.
            name = node.get('serienname') or node.text
            if not name:
                continue
            serienname = unicode(name).strip()
            result[serienname] = Serie(
                serienname,
                unicode_or_none(node.get('title')),
                unicode_or_none(node.get('url')),
                unicode_or_none(node.get('encoded')),
                node.get('format-label') == u'Kolumne',
                node.get('video') == u'yes')
        return result

    def getValues(self, context):
        return self.values.values()

    def getTitle(self, context, value):
        return value.serienname

    def getToken(self, context, value):
        return super(SerieSource, self).getToken(context, value.serienname)


class Product(AllowedBase):

    def __init__(self, id=None, title=None, vgwortcode=None,
                 href=None, target=None, label=None, show=None,
                 volume=None, location=None, centerpage=None, cp_template=None,
                 autochannel=True, relates_to=None):
        super(Product, self).__init__(id, title, None)
        self.vgwortcode = vgwortcode
        self.href = href
        self.target = target
        self.label = label
        self.show = show
        self.volume = volume
        self.location = location
        self.centerpage = centerpage
        self.cp_template = cp_template
        self.autochannel = autochannel
        self.relates_to = relates_to
        self.dependent_products = []


class ProductSource(ObjectSource, SimpleContextualXMLSource):

    config_url = 'source-products'

    @CONFIG_CACHE.cache_on_arguments()
    def _values(self):
        tree = self._get_tree()
        result = collections.OrderedDict()
        for node in tree.iterchildren('*'):
            product = Product(
                unicode(node.get('id')),
                unicode(node.text.strip()),
                unicode_or_none(node.get('vgwortcode')),
                unicode_or_none(node.get('href')),
                unicode_or_none(node.get('target')),
                unicode_or_none(node.get('label')),
                unicode_or_none(node.get('show')),
                node.get('volume', '').lower() == 'true',
                unicode_or_none(node.get('location')),
                unicode_or_none(node.get('centerpage')),
                unicode_or_none(node.get('cp_template')),
                node.get('autochannel', '').lower() != 'false',
                unicode_or_none(node.get('relates_to'))
            )
            result[product.id] = product
        self._add_dependent_products(result)
        return result

    def getTitle(self, context, value):
        return value.title

    def getToken(self, context, value):
        return super(ProductSource, self).getToken(context, value)

    def _add_dependent_products(self, products):
        """
        Add the dependent products to given products.
        Dependent products are defined in the product.xml via the "relates_to"
        attribute.
        """
        dependent_products = collections.defaultdict(list)
        main_products = []
        for value in products.values():
            if value.volume:
                main_products.append(value)
            if value.relates_to:
                dependent_products[value.relates_to] += [value]
        for product in main_products:
            product.dependent_products = dependent_products[product.id]

PRODUCT_SOURCE = ProductSource()


class BannerSource(SimpleXMLSource):

    config_url = 'source-banners'

    def getValues(self):
        tree = self._get_tree()
        return [int(node.get('paragraph')) for node
                in tree.xpath('//homepage/page_all') +
                tree.xpath('//homepage/content_ad')]


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

    def find(self, type_id):
        # XXX Should typegrokker register the interface with name=type_id
        # instead of/in addition to the dotted name?
        for iface in self.getValues():
            if iface.getTaggedValue('zeit.cms.type') == type_id:
                return iface


class AddableCMSContentTypeSource(CMSContentTypeSource):

    def getValues(self):
        import zeit.cms.content.interfaces  # break circular import
        types = (list(super(AddableCMSContentTypeSource, self).getValues()) +
                 list(interface for name, interface in
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


class StorystreamReference(AllowedBase):

    def __init__(self, id, title, available, centerpage_id):
        super(StorystreamReference, self).__init__(id, title, available)
        self.centerpage_id = centerpage_id

    @property
    def references(self):
        return zeit.cms.interfaces.ICMSContent(self.centerpage_id, None)


class StorystreamSource(ObjectSource, XMLSource):

    config_url = 'source-storystreams'

    @CONFIG_CACHE.cache_on_arguments()
    def _values(self):
        result = collections.OrderedDict()
        for node in self._get_tree().iterchildren('*'):
            id = node.get('name')
            result[id] = StorystreamReference(
                id, node.text, node.get('available'), node.get('href'))
        return result


class AccessSource(XMLSource):

    config_url = 'source-access'
    attribute = 'id'

    def translate_to_c1(self, value):
        try:
            return self._get_tree().xpath(
                '//type[@id = "{}"]/@c1_id'.format(value))[0]
        except IndexError:
            return None

ACCESS_SOURCE = AccessSource()


class PrintRessortSource(XMLSource):

    product_configuration = 'zeit.cms'
    config_url = 'source-printressorts'
    attribute = 'id'


PRINT_RESSORT_SOURCE = PrintRessortSource()
