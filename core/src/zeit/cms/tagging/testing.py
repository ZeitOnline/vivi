# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import stabledict
import zeit.cms.tagging.interfaces
import zeit.cms.tagging.tag
import zope.component


class FakeTags(stabledict.StableDict):

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
        tags.updateOrder = mock.Mock()
        tags.update = mock.Mock()

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
