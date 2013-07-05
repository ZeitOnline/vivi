# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import stabledict
import zeit.cms.repository.interfaces
import zeit.cms.tagging.interfaces
import zeit.cms.tagging.tag
import zope.component
import zope.interface


NAMESPACE = "http://namespaces.zeit.de/CMS/tagging"
KEYWORD_PROPERTY = ('testtags', NAMESPACE)


class DummyTagger(object):

    zope.component.adapts(zeit.cms.repository.interfaces.IDAVContent)
    zope.interface.implements(zeit.cms.tagging.interfaces.ITagger)

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
        return self.whitelist[key]

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

    @property
    def pinned(self):
        pass


class FakeTags(stabledict.StableDict):

    def __init__(self):
        super(FakeTags, self).__init__()
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


class TaggingHelper(object):
    """Mixin for tests which need some tagging infrastrucutre."""

    def get_tag(self, code):
        tag = zeit.cms.tagging.tag.Tag(code, code)
        return tag

    def setup_tags(self, *codes):
        tags = FakeTags()
        for code in codes:
            tags[code] = self.get_tag(code)
        patcher = mock.patch('zeit.cms.tagging.interfaces.ITagger')
        self.addCleanup(patcher.stop)
        self.tagger = patcher.start()
        self.tagger.return_value = tags

        whitelist = zope.component.queryUtility(
            zeit.cms.tagging.interfaces.IWhitelist)
        if whitelist is not None:  # only when ZCML is loaded
            for tag in tags.values():
                whitelist[tag.code] = tag

            def remove_tags_from_whitelist():
                for code in tags:
                    del whitelist[code]
            self.addCleanup(remove_tags_from_whitelist)

        return tags
