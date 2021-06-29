from unittest import mock
import collections
import lxml.objectify
import zeit.cms.repository.interfaces
import zeit.cms.tagging.interfaces
import zeit.cms.tagging.tag
import zope.component
import zope.interface


NAMESPACE = "http://namespaces.zeit.de/CMS/tagging"
KEYWORD_PROPERTY = ('testtags', NAMESPACE)


@zope.component.adapter(zeit.cms.repository.interfaces.IDAVContent)
@zope.interface.implementer(zeit.cms.tagging.interfaces.ITagger)
class DummyTagger:

    def __init__(self, context):
        self.context = context

    @property
    def whitelist(self):
        return zope.component.getUtility(
            zeit.cms.tagging.interfaces.IWhitelist)

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
                'Must pass in the same keys already present %r, not %r'
                % (self.keys(), order))
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

    tags = {
        'testtag': 'Testtag',
        'testtag2': 'Testtag2',
        'testtag3': 'Testtag3',
    }
    location_tags = {
        'hannover': 'Hannover',
        'paris': 'Paris'
    }

    def search(self, term):
        term = term.lower()
        return [FakeTag(code=k, label=v)
                for k, v in self.tags.items() if term in v.lower()]

    def locations(self, term):
        term = term.lower()
        return [FakeTag(code=key, label=label)
                for key, label in self.location_tags.items()
                if term in label.lower()]

    def get(self, id):
        if id in self.tags:
            return FakeTag(code=id, label=self.tags[id])
        return None


class FakeTags(collections.OrderedDict):

    def __init__(self):
        super().__init__()
        self.updateOrder = mock.Mock()
        self.update = mock.Mock()

    def __contains__(self, key):
        return key in list(self)

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
        return {x.uniqueId: live_prefix + x.link
                for x in self.values() if x.link}

    def to_xml(self):
        node = lxml.objectify.E.tags(*[
            lxml.objectify.E.tag(x.label) for x in self.values()])
        return node


@zope.interface.implementer(zeit.cms.tagging.interfaces.ITag)
class FakeTag:
    """Fake implementation of ITag for tests."""

    def __init__(self, code, label):
        self.label = label
        self.code = code
        self.pinned = False
        self.__name__ = self.code  # needed to fulfill `ICMSContent`
        self.link = None

    @property
    def uniqueId(self):
        return (zeit.cms.tagging.interfaces.ID_NAMESPACE +
                self.code.encode('unicode_escape').decode('ascii'))

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.code == other.code and self.pinned == other.pinned


class TaggingHelper:
    """Mixin for tests which need some tagging infrastrucutre."""

    def get_tag(self, code):
        tag = FakeTag(code=code, label=code)
        return tag

    def setup_tags(self, *codes):
        tags = FakeTags()
        for code in codes:
            tags[code] = self.get_tag(code)
        patcher = mock.patch('zeit.cms.tagging.interfaces.ITagger')
        self.addCleanup(patcher.stop)
        self.tagger = patcher.start()
        self.tagger.return_value = tags
        self.whitelist_tags = {tag.code: tag.label for tag in tags.values()}

        whitelist = zope.component.queryUtility(
            zeit.cms.tagging.interfaces.IWhitelist)
        if whitelist is not None:  # only when ZCML is loaded
            original_tags = whitelist.tags
            whitelist.tags = self.whitelist_tags

            def restore_original_tags_on_whitelist():
                whitelist.tags = original_tags
            self.addCleanup(restore_original_tags_on_whitelist)
        return tags

    def add_keyword_by_autocomplete(self, text, form_prefix='form'):
        self.add_by_autocomplete(
            text, 'id=%s.keywords.add' % form_prefix)

    def add_topicpage_link(self, tag):
        tag.link = 'thema/%s' % tag.label.lower()
