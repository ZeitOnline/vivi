from zeit.retresco.tag import Tag
import grokcore.component as grok
import logging
import lxml.etree
import lxml.objectify
import zeit.cms.content.dav
import zeit.cms.tagging.interfaces
import zeit.connector.interfaces
import zeit.retresco.interfaces
import zope.component


NAMESPACE = "http://namespaces.zeit.de/CMS/tagging"
KEYWORD_PROPERTY = ('rankedTags', NAMESPACE)
DISABLED_PROPERTY = ('disabled', NAMESPACE)
DISABLED_SEPARATOR = '\x09'
PINNED_PROPERTY = ('pinned', NAMESPACE)

log = logging.getLogger(__name__)


class Tagger(zeit.cms.content.dav.DAVPropertiesAdapter):
    """Serializes keywords to an XML structure and stores it in a DAV-Property.

    The serialization format (including pinned and disabled keywords) is
    actually backwards compatible with zeit.intrafind, but since the TMS uses
    different IDs for keywords, switching to retresco means that
    pinned+disabled keywords will effectively be reset. (Keywords that are
    assigned to content already will remain usable, though, since the label is
    pretty much the only interesting property.)

    We need to read/write all tags from/to xml for every operation, since
    adapting to ``ITagger`` returns a *different* Tagger each time, so we
    cannot (easily) cache anything on the Tagger instance.

    There are also '<rankedTags>' in the XML of ``context`` but these are
    written by ``zeit.cms.tagging.tag.add_ranked_tags_to_head``. At this point,
    the information about pinned and disabled tags is omitted, as it is only
    needed in vivi.

    """

    grok.implements(zeit.cms.tagging.interfaces.ITagger)

    def __iter__(self):
        tags = self.to_xml()
        if tags is None:
            return iter(())
        return (Tag(x.text, x.get('type', '')).code
                for x in tags.iterchildren())

    def __len__(self):
        return len(list(self.__iter__()))

    def __getitem__(self, key):
        node = self._find_tag_node(key)
        tag = self._create_tag(unicode(node), node.get('type', ''))
        return tag

    def __setitem__(self, key, value):
        tags = self.to_xml()
        if tags is None:
            E = lxml.objectify.ElementMaker(namespace=NAMESPACE)
            root = E.rankedTags()
            tags = E.rankedTags()
            root.append(tags)
        # XXX the handling of namespaces here seems chaotic
        E = lxml.objectify.ElementMaker()
        tags.append(E.tag(value.label, type=value.entity_type or ''))
        dav = zeit.connector.interfaces.IWebDAVProperties(self)
        dav[KEYWORD_PROPERTY] = lxml.etree.tostring(tags.getroottree())

    def values(self):
        tags = self.to_xml()
        if tags is None:
            return iter(())
        return (self._create_tag(unicode(node), node.get('type', ''))
                for node in tags.iterchildren())

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
                'Must pass in the same keys already present %r, not %r'
                % (list(self), keys))
        orderd = []
        tags = self.to_xml()
        for key in keys:
            tag = self._find_tag_node(key, tags)
            orderd.append(tag)
            tags.remove(tag)
        tags.extend(orderd)
        dav = zeit.connector.interfaces.IWebDAVProperties(self)
        dav[KEYWORD_PROPERTY] = lxml.etree.tostring(tags.getroottree())

    def __delitem__(self, key):
        node = self._find_tag_node(key)
        node.getparent().remove(node)
        dav = zeit.connector.interfaces.IWebDAVProperties(self)
        dav[KEYWORD_PROPERTY] = lxml.etree.tostring(node.getroottree())
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

    def to_xml(self):
        dav = zeit.connector.interfaces.IWebDAVProperties(self)
        try:
            tags = lxml.objectify.fromstring(dav.get(KEYWORD_PROPERTY, ''))
        except lxml.etree.XMLSyntaxError:
            return None
        if tags.tag != '{{{1}}}{0}'.format(*KEYWORD_PROPERTY):
            return None
        return tags.getchildren()[0]

    def _find_tag_node(self, key, tags=None):
        if tags is None:
            tags = self.to_xml()
        if tags is None:
            raise KeyError(key)

        node = [x for x in tags.iterchildren()
                if Tag(x.text, x.get('type', '')).code == key]
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

    def update(self):
        """Update the keywords with generated keywords from retresco.

        A number of reasonable keywords are retrieved from retresco. This set
        is reduced by the disabled keywords and enriched by the pinned
        keywords. The resulting set is finally written to the DAV property.

        """
        log.info('Updating tags for %s', self.context.uniqueId)
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        keywords = tms.extract_keywords(self.context)

        E = lxml.objectify.ElementMaker(namespace=NAMESPACE)
        root = E.rankedTags()
        new_tags = E.rankedTags()
        root.append(new_tags)

        # XXX the handling of namespaces here seems chaotic
        E = lxml.objectify.ElementMaker()
        new_codes = set()
        for tag in keywords:
            if tag.code in self.disabled:
                continue
            new_codes.add(tag.code)
            new_tags.append(E.tag(tag.label, type=tag.entity_type or ''))

        old_tags = self.to_xml()
        for code in self.pinned:
            if code not in new_codes:
                pinned_tag = self._find_tag_node(code, old_tags)
                new_tags.append(pinned_tag)

        dav = zeit.connector.interfaces.IWebDAVProperties(self)
        dav[KEYWORD_PROPERTY] = lxml.etree.tostring(root.getroottree())
        dav[DISABLED_PROPERTY] = u''
