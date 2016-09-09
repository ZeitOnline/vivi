from zeit.cms.checkout.helper import checked_out
import gocept.runner
import grokcore.component as grok
import logging
import lxml.builder
import lxml.objectify
import xml.sax.saxutils
import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.cms.tagging.interfaces
import zeit.cms.workflow.interfaces
import zeit.connector.interfaces
import zeit.retresco.interfaces
import zope.component
import zope.interface


NAMESPACE = "http://namespaces.zeit.de/CMS/tagging"
KEYWORD_PROPERTY = ('rankedTags', NAMESPACE)
DISABLED_PROPERTY = ('disabled', NAMESPACE)
DISABLED_SEPARATOR = '\x09'
PINNED_PROPERTY = ('pinned', NAMESPACE)

log = logging.getLogger(__name__)


class Tagger(zeit.cms.content.dav.DAVPropertiesAdapter):
    """Serializes keywords to an XML structure and stores it as a DAV property.

    The serialization format (including pinned and disabled keywords) is
    actually backwards compatible with zeit.intrafind, but since the TMS uses
    different IDs for keywords, switching to retresco means that
    pinned+disabled keywords will effectively be reset. (Keywords that are
    assigned to content already will remain usable, though, since the label is
    pretty much the only interesting property.)
    """

    grok.implements(zeit.cms.tagging.interfaces.ITagger)

    def __iter__(self):
        tags = self.to_xml()
        if tags is None:
            return iter(())
        return (x.get('uuid') for x in tags.iterchildren() if x.get('uuid'))

    def __len__(self):
        return len(list(self.__iter__()))

    def __getitem__(self, key):
        node = self._find_tag_node(key)

        tag = Tag(unicode(node), node.get('type'))
        if tag.code in self.pinned:
            tag.pinned = True
        tag.__parent__ = self
        tag.__name__ = tag.code
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
        return (self[code] for code in self)

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
        node = tags.xpath('//tag[@uuid = {0}]'.format(
            xml.sax.saxutils.quoteattr(key)))
        if not node:
            raise KeyError(key)
        return node[0]

    def update(self):
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
            new_tags.append(E.tag(
                tag.label, uuid=tag.code, type=tag.entity_type or '',
                url_value=tag.url_value or ''))

        old_tags = self.to_xml()
        for code in self.pinned:
            if code not in new_codes:
                pinned_tag = self._find_tag_node(code, old_tags)
                new_tags.append(pinned_tag)

        dav = zeit.connector.interfaces.IWebDAVProperties(self)
        dav[KEYWORD_PROPERTY] = lxml.etree.tostring(root.getroottree())
        dav[DISABLED_PROPERTY] = u''


@gocept.runner.once(principal=gocept.runner.from_config(
    'zeit.retresco', 'topiclist-principal'))
def update_topiclist():
    _update_topiclist()


def _update_topiclist():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.retresco')
    keywords = zeit.cms.interfaces.ICMSContent(config['topiclist'], None)
    if not zeit.content.rawxml.interfaces.IRawXML.providedBy(keywords):
        raise ValueError(
            '%s is not a raw xml document' % config['topiclist'])
    with checked_out(keywords) as co:
        log.info('Retrieving all topic pages from TMS')
        co.xml = _build_topic_xml()
    zeit.cms.workflow.interfaces.IPublish(keywords).publish(async=False)


def _build_topic_xml():
    tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
    E = lxml.builder.ElementMaker()
    root = E.topics()
    for row in tms.get_all_topicpages():
        # XXX What other attributes might be interesting to use in a
        # dynamicfolder template?
        root.append(E.topic(
            row['title'],
            id=zeit.cms.interfaces.normalize_filename(row['name'])))
    return root


class Tag(object):
    """Representation of a keyword."""

    zope.interface.implements(zeit.cms.tagging.interfaces.ITag,
                              zeit.cms.interfaces.ICMSContent)

    SEPARATOR = u':=)'

    def __init__(self, label, entity_type, pinned=False):
        self.label = label
        self.entity_type = entity_type
        self.pinned = pinned
        self.code = u''.join((entity_type, self.SEPARATOR, label))

    @classmethod
    def from_code(cls, code):
        entity_type, sep, label = code.partition(cls.SEPARATOR)
        return cls(label, entity_type)

    def __eq__(self, other):
        # XXX this is not a generic equality check. From a domain perspective,
        # two tags are the same when their codes are the same. However, since
        # we want to edit ``pinned``, and formlib compares the *list* of
        # keywords, which uses == on the items, we need to include pinned here.
        if other is None:
            return False
        return self.code == other.code and self.pinned == other.pinned

    @property
    def uniqueId(self):
        return (zeit.cms.tagging.interfaces.ID_NAMESPACE +
                self.code.encode('unicode_escape'))


class Whitelist(object):
    """Search for known keywords using the Retresco API."""

    zope.interface.implements(zeit.cms.tagging.interfaces.IWhitelist)

    def search(self, term):
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        return tms.get_keywords(term)

    def get(self, id):
        return Tag.from_code(id)
