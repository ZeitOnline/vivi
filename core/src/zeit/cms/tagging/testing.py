# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import mock

class TaggingHelper(object):
    """Mixin for tests which need some tagging infrastrucutre."""

    def get_tag(self, code):
        tag = mock.Mock()
        tag.code = tag.label = code
        tag.disabled = False
        return tag

    def setup_tags(self, *codes):
        import stabledict
        class Tags(stabledict.StableDict):
            pass
        tags = Tags()
        for code in codes:
            tags[code] = self.get_tag(code)
        patcher = mock.patch('zeit.cms.tagging.interfaces.ITagger')
        self.addCleanup(patcher.stop)
        self.tagger = patcher.start()
        self.tagger.return_value = tags
        tags.updateOrder = mock.Mock()
        tags.update = mock.Mock()
        return tags

