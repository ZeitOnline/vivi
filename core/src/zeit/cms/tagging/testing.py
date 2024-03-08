from unittest import mock
import collections

import lxml.builder
import zope.component
import zope.interface

from zeit.cms.tagging.tag import XML_NS, Tag
import zeit.cms.repository.interfaces
import zeit.cms.tagging.interfaces


NAMESPACE = 'http://namespaces.zeit.de/CMS/tagging'
KEYWORD_PROPERTY = ('testtags', NAMESPACE)


@zope.component.adapter(zeit.cms.repository.interfaces.IDAVContent)
@zope.interface.implementer(zeit.cms.tagging.interfaces.ITagger)
class DummyTagger:
    def __init__(self, context):
        self.context = context

    @property
    def whitelist(self):
        return zope.component.getUtility(zeit.cms.tagging.interfaces.IWhitelist)

    @property
    def dav_properties(self):
        return zeit.connector.interfaces.IWebDAVProperties(self.context)

    def __iter__(self):
        return iter(self.keys())

    def __len__(self):
        return len(self.keys())

    def __contains__(self, key):
        return key in self.keys()

    def keys(self):
        keys = self.dav_properties.get(KEYWORD_PROPERTY, '').split('|')
        return tuple(keys) if keys != [''] else ()

    def values(self):
        return (self[x] for x in self.keys())

    def __getitem__(self, key):
        if key not in self.keys():
            raise KeyError(key)
        return self.whitelist.get(key)

    def __setitem__(self, key, value):
        keys = list(self.keys())
        if key not in keys:
            keys.append(key)
            self.dav_properties[KEYWORD_PROPERTY] = '|'.join(keys)

    def __delitem__(self, key):
        keys = list(self.keys())
        keys.remove(key)
        self.dav_properties[KEYWORD_PROPERTY] = '|'.join(keys)

    def updateOrder(self, order):
        order = list(order)  # people are fond of passing in generators
        if set(order) != set(self.keys()):
            raise ValueError(
                'Must pass in the same keys already present %r, not %r' % (self.keys(), order)
            )
        self.dav_properties[KEYWORD_PROPERTY] = '|'.join(order)

    def update(self):
        pass

    def set_pinned(self, keys):
        pass

    def to_xml(self):
        return None

    links = {}
    pinned = {}


@zope.interface.implementer(zeit.cms.tagging.interfaces.IWhitelist)
class DummyWhitelist:
    tags = [
        'Testtag',
        'Testtag2',
        'Testtag3',
    ]
    location_tags = [
        'Hannover',
        'Paris',
    ]
    entity_type = 'test'

    def search(self, term):
        term = term.lower()
        return [Tag(label, self.entity_type) for label in self.tags if term in label.lower()]

    def locations(self, term):
        term = term.lower()
        return [
            Tag(label, self.entity_type) for label in self.location_tags if term in label.lower()
        ]

    def get(self, tag_id):
        label = tag_id.replace('test%s' % Tag.SEPARATOR, '')
        if label in self.tags:
            return Tag(label, self.entity_type)
        return None


class FakeTags(collections.OrderedDict):
    def __init__(self):
        super().__init__()
        self.updateOrder = mock.Mock()
        self.update = mock.Mock()

    def _key(self, key):
        if Tag.SEPARATOR not in key:
            key = ''.join([DummyWhitelist.entity_type, Tag.SEPARATOR, key])
        return key

    def __getitem__(self, key):
        return super().__getitem__(self._key(key))

    def __setitem__(self, key, value):
        return super().__setitem__(self._key(key), value)

    def __delitem__(self, key):
        return super().__delitem__(self._key(key))

    def __contains__(self, key):
        return self._key(key) in list(self)

    def set_pinned(self, keys):
        for tag in self.values():
            tag.pinned = tag.code in keys

    @property
    def pinned(self):
        return [x.code for x in self.values() if x.pinned]

    @property
    def links(self):
        config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
        live_prefix = config['live-prefix']
        return {x.uniqueId: live_prefix + x.link for x in self.values() if x.link}

    def to_xml(self):
        E = lxml.builder.ElementMaker(namespace=XML_NS)
        node = E.rankedTags(*[lxml.builder.E.tag(x.label) for x in self.values()])
        return node


class TaggingHelper:
    """Mixin for tests which need some tagging infrastrucutre."""

    def setup_tags(self, *labels):
        tags = FakeTags()
        for label in labels:
            tags[label] = Tag(label, DummyWhitelist.entity_type)
        patcher = mock.patch('zeit.cms.tagging.interfaces.ITagger')
        self.addCleanup(patcher.stop)
        self.tagger = patcher.start()
        self.tagger.return_value = tags

        whitelist = zope.component.queryUtility(zeit.cms.tagging.interfaces.IWhitelist)
        if whitelist is not None:  # only when ZCML is loaded
            original_tags = whitelist.tags
            whitelist.tags = list(labels)

            def restore_original_tags_on_whitelist():
                whitelist.tags = original_tags

            self.addCleanup(restore_original_tags_on_whitelist)
        return tags

    def add_keyword_by_autocomplete(self, text, form_prefix='form'):
        self.add_by_autocomplete(text, 'id=%s.keywords.add' % form_prefix)

    def add_topicpage_link(self, tag):
        tag.link = 'thema/%s' % tag.label.lower()
