from collections import defaultdict
from functools import reduce
import logging
import operator
import os
import urllib.request
import xml.sax.saxutils

import lxml.objectify
import pyramid_dogpile_cache2
import zc.sourcefactory.basic
import zc.sourcefactory.contextual
import zope.component
import zope.dottedname
import zope.i18n
import zope.security.proxy

from zeit.cms.i18n import MessageFactory as _
from zeit.cms.interfaces import CONFIG_CACHE, FEATURE_CACHE
import zeit.cms.config
import zeit.cms.interfaces
import zeit.connector.interfaces


logger = logging.getLogger('zeit.cms.content.sources')

try:
    import zope.testing.cleanup

    zope.testing.cleanup.addCleanUp(pyramid_dogpile_cache2.clear)
except ImportError:
    pass


def load(url):
    if url.startswith(zeit.cms.interfaces.ID_NAMESPACE):
        connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
        return connector[url].data
    else:
        req = urllib.request.Request(url, headers={'accept': 'application/octet-stream'})
        return urllib.request.urlopen(req)


class OverridableURLConfiguration:
    product_configuration = 'zeit.cms'
    config_url = NotImplemented
    default_filename = NotImplemented

    @property
    def url(self):
        try:
            return zeit.cms.config.required(self.product_configuration, self.config_url)
        except KeyError:
            if self.default_filename is NotImplemented:
                raise
            base = zeit.cms.config.required('zeit.cms', 'config-base-url').rstrip('/')
            return '%s/%s' % (base, self.default_filename)


class CachedXMLBase(OverridableURLConfiguration):
    def _get_tree(self):
        return self._get_tree_from_url(self.url)

    @CONFIG_CACHE.cache_on_arguments()
    def _get_tree_from_url(self, url):
        __traceback_info__ = (url,)
        logger.debug('Getting %s' % url)
        return lxml.objectify.parse(load(url)).getroot()


class ShortCachedXMLBase(CachedXMLBase):
    # Unfortunately needs copy&paste to change the cache region.
    @FEATURE_CACHE.cache_on_arguments()
    def _get_tree_from_url(self, url):
        __traceback_info__ = (url,)
        logger.debug('Getting %s' % url)
        return lxml.objectify.parse(load(url)).getroot()


class SimpleXMLSourceBase(CachedXMLBase):
    def getValues(self):
        xml = self._get_tree()
        return [str(x).strip() for x in xml.iterchildren('*')]


class XMLSource(SimpleXMLSourceBase, zc.sourcefactory.contextual.BasicContextualSourceFactory):
    """This source should be used in most cases."""

    # NOTE: this source is contextual to be able to set a default for a field
    # using the source even while there is no product config.

    attribute = NotImplemented
    xpath = './*'
    title_xpath = '//*'

    def getValues(self, context):
        tree = self._get_tree()
        return [
            str(node.get(self.attribute))
            for node in tree.xpath(self.xpath)
            if self.isAvailable(node, context)
        ]

    def isAvailable(self, node, context):
        # NOTE: the *default* value must not use ``available``, since e.g.
        # newly created objects do not have their marker interfaces yet when
        # they are assigned the default value, which would lead to
        # ConstraintNotSatisfied errors.
        for iface in parse_available_interface_list(node.get('available')):
            if iface.providedBy(context):
                return True
        return False

    def getTitle(self, context, value):
        __traceback_info__ = (value,)
        tree = self._get_tree()
        nodes = tree.xpath(
            '%s[@%s= %s]' % (self.title_xpath, self.attribute, xml.sax.saxutils.quoteattr(value))
        )
        if nodes:
            return self._get_title_for(nodes[0])
        return value

    def _get_title_for(self, node):
        return str(node.text).strip()


def parse_available_interface_list(text):
    result = []
    if text is None:
        text = 'zope.interface.Interface'
    for iface in text.split():
        try:
            result.append(zope.dottedname.resolve.resolve(iface))
        except ImportError:
            continue
    return result


class SimpleXMLSource(SimpleXMLSourceBase, zc.sourcefactory.basic.BasicSourceFactory):
    """A simple xml source."""


class SimpleContextualXMLSource(
    SimpleXMLSourceBase, zc.sourcefactory.contextual.BasicContextualSourceFactory
):
    """A simple contextual xml source."""

    def getValues(self, context):
        return super().getValues()


class SimpleFixedValueSource(zc.sourcefactory.basic.BasicSourceFactory):
    values = NotImplemented

    def __init__(self, values=None):
        if values is not None:
            self.values = values
        if not hasattr(self.values, 'keys'):
            self.values = {x: _(x) for x in self.values}

    def getValues(self):
        return self.values.keys()

    def getTitle(self, value):
        return self.values[value]


class IObjectSource(zope.schema.interfaces.IIterableSource):
    pass


@zope.interface.implementer(IObjectSource)
class FactoredObjectSource(zc.sourcefactory.source.FactoredContextualSource):
    def __contains__(self, value):
        id = getattr(value, 'id', None)
        if id is None:
            return False
        return self.find(id) is not None

    def find(self, id):
        return self.factory.find(self.context, id)

    def find_by_property(self, property_name, value):
        return self.factory.find_by_property(self.context, property_name, value)


class ObjectSource(zc.sourcefactory.factories.ContextualSourceFactory):
    source_class = FactoredObjectSource

    def _values(self):
        raise NotImplementedError()

    def getTitle(self, context, value):
        return getattr(value, 'title', value)

    def getToken(self, context, value):
        return getattr(value, 'id', value)

    def isAvailable(self, value, context):
        return value.is_allowed(context)

    def getValues(self, context):
        return [x for x in self._values().values() if self.isAvailable(x, context)]

    def find(self, context, id):
        value = self._values().get(id)
        if (
            not value
            or not self.isAvailable(value, context)
            or not self.filterValue(context, value)
        ):
            return None
        return value

    def find_by_property(self, context, property_name, value):
        for item in self._values().values():
            if getattr(item, property_name) == value:
                return item
        return None


class AllowedBase:
    def __init__(self, id, title, available):
        self.id = id
        self.title = title
        self.available_ifaces = parse_available_interface_list(available)

    def is_allowed(self, context):
        if not self.available_ifaces:
            return False
        for iface in self.available_ifaces:
            if iface.providedBy(context):
                return True
        return False

    def __eq__(self, other):
        return zope.security.proxy.isinstance(other, self.__class__) and self.id == other.id


class FolderItemSource(zc.sourcefactory.basic.BasicSourceFactory):
    product_configuration = NotImplemented
    config_url = NotImplemented
    interface = None

    class source_class(zc.sourcefactory.source.FactoredSource):
        def find(self, name):
            return self.factory.find(name)

    @property
    def folder(self):
        id = zeit.cms.config.required(self.product_configuration, self.config_url)
        return zeit.cms.interfaces.ICMSContent(id)

    def getValues(self):
        values = self.folder.values()
        if self.interface is not None:
            values = [x for x in values if self.interface.providedBy(x)]
        return values

    def getTitle(self, value):
        return value.title

    def getToken(self, value):
        return value.__name__

    def find(self, id):
        if not id:
            return None
        return self.folder.get(id)


class SimpleDictSource(zc.sourcefactory.basic.BasicSourceFactory):
    values = {}

    def getValues(self):
        return self.values.keys()

    def getTitle(self, value):
        return self.values.get(value, value)


class ContextualDictSource(zc.sourcefactory.contextual.BasicContextualSourceFactory):
    values = {}

    def getValues(self, context):
        return self.values.keys()

    def getTitle(self, context, value):
        return self.values.get(value, value)


class RessortSource(XMLSource):
    config_url = 'source-ressorts'
    default_filename = 'ressorts.xml'
    attribute = 'name'
    title_xpath = '/ressorts/ressort'

    def _get_title_for(self, node):
        return str(node['title'])


class ParentChildSource(XMLSource):
    child_tag = NotImplemented
    parent_node_xpath = NotImplemented
    parent_value_iface = NotImplemented
    parent_value_key = NotImplemented

    def getValues(self, context):
        __traceback_info__ = (context,)
        parent_nodes = self._get_parent_nodes(context)
        child_nodes = reduce(operator.add, [node.findall(self.child_tag) for node in parent_nodes])
        result = {
            str(node.get(self.attribute)) for node in child_nodes if self.isAvailable(node, context)
        }
        return result

    def getTitle(self, context, value):
        tree = self._get_tree()
        parent_value = self._get_parent_value(context)
        if parent_value is None:
            nodes = tree.xpath(
                '//{child_tag}[@{attribute} = {value}]'.format(
                    child_tag=self.child_tag,
                    attribute=self.attribute,
                    value=xml.sax.saxutils.quoteattr(value),
                )
            )
        else:
            nodes = tree.xpath(
                '{parent_node_xpath}[@{attribute} = {master}]'
                '/{child_tag}[@{attribute} = {value}]'.format(
                    parent_node_xpath=self.parent_node_xpath,
                    attribute=self.attribute,
                    child_tag=self.child_tag,
                    master=xml.sax.saxutils.quoteattr(parent_value),
                    value=xml.sax.saxutils.quoteattr(value),
                )
            )
        if nodes:
            return str(self._get_title_for(nodes[0]))
        return value

    def _get_parent_nodes(self, context):
        tree = self._get_tree()
        all_nodes = tree.xpath(self.parent_node_xpath)
        parent_value = self._get_parent_value(context)
        if not parent_value:
            return all_nodes

        nodes = tree.xpath(
            '{parent_node_xpath}[@{attribute} = "{value}"]'.format(
                parent_node_xpath=self.parent_node_xpath,
                attribute=self.attribute,
                # XXX not sure why we do manual quoting instead of quoteattr
                # here, doesn't feel as it was thought through. There's a
                # random doctest example about 'Bildung & Beruf' however that
                # breaks if I change it.
                value=parent_value,
            )
        )
        if not nodes:
            return None
        # XXX assert len(nodes) == 1
        return nodes

    def _get_parent_value(self, context):
        if isinstance(context, str):
            return context
        if zeit.cms.interfaces.ICMSContent.providedBy(context):
            return None
        data = self.parent_value_iface(context, None)
        if data is None:
            return None
        return getattr(data, self.parent_value_key)


class SubRessortSource(ParentChildSource):
    config_url = RessortSource.config_url
    default_filename = RessortSource.default_filename
    attribute = RessortSource.attribute
    child_tag = 'subnavigation'
    parent_node_xpath = '/ressorts/ressort'
    parent_value_key = 'ressort'

    @property
    def parent_value_iface(self):
        # prevent circular import
        import zeit.cms.content.interfaces

        return zeit.cms.content.interfaces.ICommonMetadata

    def _get_title_for(self, node):
        return str(node['title'])


class ChannelSource(XMLSource):
    config_url = 'source-channels'
    default_filename = 'channels.xml'
    attribute = 'name'
    title_xpath = '/ressorts/ressort'

    def _get_title_for(self, node):
        return str(node['title'])


class SubChannelSource(ParentChildSource):
    config_url = ChannelSource.config_url
    default_filename = ChannelSource.default_filename
    attribute = ChannelSource.attribute
    child_tag = 'subnavigation'
    parent_node_xpath = '/ressorts/ressort'
    parent_value_key = 'ressort'

    @property
    def parent_value_iface(self):
        # prevent circular import
        import zeit.cms.content.interfaces

        return zeit.cms.content.interfaces.ICommonMetadata

    def _get_parent_nodes(self, context):
        if type(context).__name__ == 'Fake':
            # for .browser.ParentChildDropdownUpdater
            return super()._get_parent_nodes(context)
        # The ``channels`` field is a list of combination values.
        # The formlib validation machinery does not give us enough context
        # to determine the master value, so we are forced to allow all values.
        # We can get away with this since the UI only offers valid subchannel
        # values (powered by ParentChildDropdownUpdater above).
        tree = self._get_tree()
        all_nodes = tree.xpath(self.parent_node_xpath)
        return all_nodes

    def _get_title_for(self, node):
        return str(node['title'])


class FeatureToggleSource(ShortCachedXMLBase, XMLSource):
    # Only contextual so we can customize source_class

    product_configuration = 'zeit.cms'
    config_url = 'feature-toggle-source'
    default_filename = 'vivi-feature-toggle.xml'

    class source_class(zc.sourcefactory.source.FactoredContextualSource):
        def find(self, name):
            return self.factory.find(name)

        def set(self, *names):  # only for tests
            self.factory.override(True, *names)

        def unset(self, *names):  # only for tests
            self.factory.override(False, *names)

    def find(self, name):
        # Allow to override toggles via environment, for local development.
        key = 'toggle_{}'.format(name)
        if key in os.environ:
            return bool(os.environ[key])

        return self._values().get(name)

    def override(self, value, *names):
        for name in names:
            # Changes are discarded between tests, as they call dogpile clear()
            self._values()[name] = value

    def getValues(self, context):
        return [k for k, v in self._values().items() if v]

    @FEATURE_CACHE.cache_on_arguments()
    def _values(self):
        tree = self._get_tree()
        result = {
            node.tag: bool(node)
            for node in tree.xpath('//*')
            if isinstance(node, lxml.objectify.BoolElement)
        }
        return result


FEATURE_TOGGLES = FeatureToggleSource()(None)


def unicode_or_none(value):
    return str(value) if value else None


class Serie(AllowedBase):
    def __init__(
        self,
        serienname=None,
        title=None,
        url=None,
        encoded=None,
        column=False,
        kind=None,
        video=False,
        fallback_image=False,
        zonaudioapp_id=None,
        color=None,
        available=None,
    ):
        super().__init__(serienname, title, available)
        self.id = serienname
        self.serienname = serienname
        self.title = title
        self.url = url
        self.encoded = encoded
        self.column = column
        self.kind = kind
        self.video = video
        self.fallback_image = fallback_image
        self.zonaudioapp_id = zonaudioapp_id
        self.color = color

    def __eq__(self, other):
        if not zope.security.proxy.isinstance(other, self.__class__):
            return False
        return self.serienname == other.serienname


class SerieSource(ObjectSource, SimpleContextualXMLSource):
    config_url = 'source-serie'
    default_filename = 'series.xml'

    @CONFIG_CACHE.cache_on_arguments()
    def _values(self):
        result = {}
        for node in self._get_tree().iterchildren('*'):
            # XXX: For compat reasons we need a fallback `serienname`.
            name = node.get('serienname') or node.text
            if not name:
                continue
            serienname = str(name).strip()
            result[serienname] = Serie(
                serienname,
                unicode_or_none(node.get('title')),
                unicode_or_none(node.get('url')),
                unicode_or_none(node.get('encoded')),
                node.get('format-label') == 'Kolumne',
                unicode_or_none(node.get('kind')),
                node.get('video') == 'yes',
                node.get('fallback_image') == 'yes',
                unicode_or_none(node.get('zonaudioapp-id')),
                unicode_or_none(node.get('color')),
                unicode_or_none(node.get('available')),
            )
        return result

    def getTitle(self, context, value):
        if not isinstance(zope.security.proxy.removeSecurityProxy(value), Serie):
            return None
        return value.serienname


class Product(AllowedBase):
    def __init__(
        self,
        id=None,
        title=None,
        vivi_title=None,
        vgwort_code=None,
        href=None,
        target=None,
        label=None,
        show=None,
        volume=None,
        location=None,
        centerpage=None,
        cp_template=None,
        autochannel=True,
        relates_to=None,
        is_news=False,
        counter=False,
    ):
        super().__init__(id, title, None)
        self.vivi_title = vivi_title
        self.vgwort_code = vgwort_code
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
        self.is_news = is_news
        self.dependent_products = []
        self.counter = counter


class ProductSource(ObjectSource, SimpleContextualXMLSource):
    config_url = 'source-products'
    default_filename = 'products.xml'

    @CONFIG_CACHE.cache_on_arguments()
    def _values(self):
        tree = self._get_tree()
        result = {}
        for node in tree.iterchildren('*'):
            product = Product(
                str(node.get('id')),
                str(node.text.strip()),
                unicode_or_none(node.get('vivi_title')),
                unicode_or_none(node.get('vgwort_code')),
                unicode_or_none(node.get('href')),
                unicode_or_none(node.get('target')),
                unicode_or_none(node.get('label')),
                unicode_or_none(node.get('show')),
                node.get('volume', '').lower() == 'true',
                unicode_or_none(node.get('location')),
                unicode_or_none(node.get('centerpage')),
                unicode_or_none(node.get('cp_template')),
                node.get('autochannel', '').lower() != 'false',
                unicode_or_none(node.get('relates_to')),
                node.get('is_news', '').lower() == 'true',
                unicode_or_none(node.get('counter')),
            )
            result[product.id] = product
        self._add_dependent_products(result)
        return result

    def _add_dependent_products(self, products):
        """
        Add the dependent products to given products.
        Dependent products are defined in the product.xml via the "relates_to"
        attribute.
        """
        dependent_products = defaultdict(list)
        main_products = []
        for value in products.values():
            if value.volume:
                main_products.append(value)
            if value.relates_to:
                dependent_products[value.relates_to] += [value]
        for product in main_products:
            product.dependent_products = dependent_products[product.id]

    def getTitle(self, context, value):
        if not isinstance(zope.security.proxy.removeSecurityProxy(value), Product):
            # Content has a stored id that is not in the config file anymore
            return value
        return value.vivi_title or value.title


PRODUCT_SOURCE = ProductSource()


class CMSContentTypeSource(ObjectSource, zc.sourcefactory.contextual.BasicContextualSourceFactory):
    class source_class(FactoredObjectSource):
        def __contains__(self, value):
            # Skip immediate superclass to get default behaviour of comparing
            # against every available value.
            return super(FactoredObjectSource, self).__contains__(value)

    def _values(self):
        return dict(zope.component.getUtilitiesFor(zeit.cms.interfaces.ICMSContentType))

    def getTitle(self, context, value):
        return value.queryTaggedValue('zeit.cms.title') or str(value)

    def getToken(self, context, value):
        return value.queryTaggedValue('zeit.cms.type') or str(value)

    def isAvailable(self, value, context):
        return True


class AddableCMSContentTypeSource(CMSContentTypeSource):
    def getValues(self, context):
        import zeit.cms.content.interfaces  # break circular import

        types = list(super().getValues(context)) + [
            interface
            for name, interface in zope.component.getUtilitiesFor(
                zeit.cms.content.interfaces.IAddableContent
            )
        ]
        by_title = {
            # XXX Hard-code language, since we don't have a request here.
            zope.i18n.translate(self.getTitle(context, x), target_language='de'): x
            for x in types
        }
        return [by_title[x] for x in sorted(by_title.keys())]

    def filterValue(self, context, value):
        import zeit.cms.type  # break circular import

        if value.queryTaggedValue('zeit.cms.addform') == zeit.cms.type.SKIP_ADD:
            return False
        permission = value.queryTaggedValue('zeit.cms.addpermission')
        if not permission:  # most content types need no special permission
            return True
        return zope.security.management.getInteraction().checkPermission(permission, context)


class PrintRessortSource(XMLSource):
    product_configuration = 'zeit.cms'
    config_url = 'source-printressorts'
    default_filename = 'print-ressorts.xml'
    attribute = 'id'


PRINT_RESSORT_SOURCE = PrintRessortSource()


class IAutocompleteSource(zope.interface.Interface):
    """Marker that this source supports autocomplete.

    Current implementation see zeit.cms.browser:js/autocomplete.js
    which uses a jQuery UI autocomplete widget and configures its URL endpoint
    by looking up zeit.cms.browser.interfaces.ISourceQueryURL(source, request)
    """
