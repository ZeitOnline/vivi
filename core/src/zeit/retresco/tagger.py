import logging

from zope.cachedescriptors.property import Lazy as cachedproperty
import grokcore.component as grok
import lxml.etree
import lxml.objectify
import zope.component

from zeit.cms.content.interfaces import WRITEABLE_ALWAYS
from zeit.cms.tagging.tag import Tag
import zeit.cms.content.dav
import zeit.cms.tagging.interfaces
import zeit.connector.interfaces
import zeit.retresco.interfaces


NAMESPACE = 'http://namespaces.zeit.de/CMS/tagging'
KEYWORD_PROPERTY = ('keywords', NAMESPACE)
DISABLED_PROPERTY = ('disabled', NAMESPACE)
DISABLED_SEPARATOR = '\x09'
PINNED_PROPERTY = ('pinned', NAMESPACE)

# To speed up indexing we do not checkout resources to update properties.
# This is why we make the keyword property writeable.
property_manager = zeit.cms.content.liveproperty.LiveProperties
for prop in [KEYWORD_PROPERTY, DISABLED_PROPERTY, PINNED_PROPERTY]:
    property_manager.register_live_property(prop[0], prop[1], WRITEABLE_ALWAYS)

log = logging.getLogger(__name__)


@grok.implementer(zeit.cms.tagging.interfaces.ITagger)
class Tagger(zeit.cms.content.dav.DAVPropertiesAdapter):
    """Serializes keywords to an XML structure and stores it in a DAV-Property.

    The serialization format (including pinned and disabled keywords) is
    backwards compatible with zeit.intrafind, since e.g. zeit.publisher relies
    on it, but we use a different DAV property to store the keywords
    (`keywords` instead of `rankedTags`).

    We need to read/write all tags from/to xml for every operation, since
    adapting to ``ITagger`` returns a *different* Tagger each time, so we
    cannot (easily) cache anything on the Tagger instance.

    There are also '<rankedTags>' in the XML of ``context`` but these are
    written by ``zeit.cms.tagging.tag.add_ranked_tags_to_head``. At this point,
    the information about pinned and disabled tags is omitted, as it is only
    needed in vivi.

    """

    def __iter__(self):
        tags = self.to_xml()
        return (Tag(x.text, x.get('type', '')).code for x in tags.iterchildren())

    def __len__(self):
        return len(list(self.__iter__()))

    def __getitem__(self, key):
        node = self._find_tag_node(key)
        tag = self._create_tag(str(node), node.get('type', ''))
        return tag

    def __setitem__(self, key, value):
        tags = self.to_xml()
        if tags is self.EMPTY_NODE:
            # XXX the handling of namespaces here seems chaotic
            E = lxml.objectify.ElementMaker(namespace=NAMESPACE)
            root = E.rankedTags()
            tags = E.rankedTags()
            root.append(tags)
        tags.append(self._serialize_tag(value))
        dav = zeit.connector.interfaces.IWebDAVProperties(self)
        dav[KEYWORD_PROPERTY] = lxml.etree.tostring(tags.getroottree(), encoding=str)

    def values(self):
        tags = self.to_xml()
        return (self._create_tag(str(node), node.get('type', '')) for node in tags.iterchildren())

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self):
        raise NotImplementedError()

    def items(self):
        raise NotImplementedError()

    def __contains__(self, key):
        return key in list(self)

    def updateOrder(self, keys):
        keys = list(keys)  # in case we've got a generator
        if set(keys) != set(self):
            raise ValueError(
                'Must pass in the same keys already present %r, not %r' % (list(self), keys)
            )
        orderd = []
        tags = self.to_xml()
        for key in keys:
            tag = self._find_tag_node(key, tags)
            orderd.append(tag)
            tags.remove(tag)
        tags.extend(orderd)
        dav = zeit.connector.interfaces.IWebDAVProperties(self)
        dav[KEYWORD_PROPERTY] = lxml.etree.tostring(tags.getroottree(), encoding=str)

    def __delitem__(self, key):
        node = self._find_tag_node(key)
        node.getparent().remove(node)
        dav = zeit.connector.interfaces.IWebDAVProperties(self)
        dav[KEYWORD_PROPERTY] = lxml.etree.tostring(node.getroottree(), encoding=str)
        self._disable(key)

    def set_pinned(self, keys):
        dav = zeit.connector.interfaces.IWebDAVProperties(self)
        dav[PINNED_PROPERTY] = DISABLED_SEPARATOR.join(keys)

    @property
    def pinned(self):
        dav = zeit.connector.interfaces.IWebDAVProperties(self)
        value = dav.get(PINNED_PROPERTY, '')
        if not value:
            return ()
        return tuple(value.split(DISABLED_SEPARATOR))

    @property
    def disabled(self):
        dav = zeit.connector.interfaces.IWebDAVProperties(self)
        disabled = dav.get(DISABLED_PROPERTY)
        if not disabled:
            return ()
        return tuple(disabled.split(DISABLED_SEPARATOR))

    def _disable(self, key):
        dav = zeit.connector.interfaces.IWebDAVProperties(self)
        disabled = self.disabled + (key,)
        dav[DISABLED_PROPERTY] = DISABLED_SEPARATOR.join(disabled)

    EMPTY_NODE = lxml.objectify.XML('<empty/>')

    def to_xml(self):
        dav = zeit.connector.interfaces.IWebDAVProperties(self)
        try:
            tags = lxml.objectify.fromstring(dav.get(KEYWORD_PROPERTY, ''))
        except lxml.etree.XMLSyntaxError:
            return self.EMPTY_NODE
        if tags.tag != '{%s}rankedTags' % KEYWORD_PROPERTY[1]:
            return self.EMPTY_NODE
        return tags.getchildren()[0]

    def _find_tag_node(self, key, tags=None):
        if tags is None:
            tags = self.to_xml()
        if tags is self.EMPTY_NODE:
            raise KeyError(key)

        node = [x for x in tags.iterchildren() if Tag(x.text, x.get('type', '')).code == key]
        if not node:
            raise KeyError(key)
        return node[0]

    def _create_tag(self, label, entity_type):
        tag = Tag(label, entity_type)
        if tag.code in self.pinned:
            tag.pinned = True
        # XXX it is not understood by the writer, whether we really need this.
        # It was kept from the former implementation in `zeit.cms.tagging`.
        tag.__parent__ = self
        return tag

    def _serialize_tag(self, tag):
        E = lxml.objectify.ElementMaker()
        return E.tag(tag.label, type=tag.entity_type or '')

    def _find_pinned_tags(self):
        xml = self.to_xml()
        result = []
        for code in self.pinned:
            try:
                node = self._find_tag_node(code, xml)
                result.append(self._create_tag(str(node), node.get('type', '')))
            except KeyError:
                pass
        return result

    def update(self, keywords=None, clear_disabled=True):
        """Update the keywords with generated keywords from retresco.

        A number of reasonable keywords are retrieved from retresco. This set
        is reduced by the disabled keywords and enriched by the pinned
        keywords. The resulting set is finally written to the DAV property.
        """
        log.info('Updating tags for %s', self.context.uniqueId)
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)

        if keywords is None:
            keywords = tms.extract_keywords(self.context)

        E = lxml.objectify.ElementMaker(namespace=NAMESPACE)
        root = E.rankedTags()
        new_tags = E.rankedTags()
        root.append(new_tags)

        new_codes = set()
        for tag in keywords:
            if tag.code in self.disabled:
                continue
            new_codes.add(tag.code)
            new_tags.append(self._serialize_tag(tag))

        for tag in self._find_pinned_tags():
            if tag.code not in new_codes:
                new_tags.append(self._serialize_tag(tag))

        dav = zeit.connector.interfaces.IWebDAVProperties(self)
        dav[KEYWORD_PROPERTY] = lxml.etree.tostring(root.getroottree(), encoding=str)
        if clear_disabled:
            dav[DISABLED_PROPERTY] = ''

    @cachedproperty
    def links(self):
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
        live_prefix = config['live-prefix']
        result = {}
        for tag in tms.get_article_topiclinks(self.context, published=False):
            if tag.link:
                result[tag.uniqueId] = live_prefix + tag.link
            else:
                result[tag.uniqueId] = None
        return result
