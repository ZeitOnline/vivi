# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.testing import copy_inherited_functions
import zeit.cms.testing
import zeit.cms.content.contentsource


class ContentSourceBase(object):

    source = zeit.cms.content.contentsource.CMSContentSource()
    expected_types = [
        'channel', 'collection', 'file', 'testcontenttype', 'unknown']

    def test_get_check_types(self):
        self.assertEquals(
            self.expected_types,
            sorted(self.source.get_check_types()))


class FolderSourceTest(ContentSourceBase,
                       zeit.cms.testing.FunctionalTestCase):

    source = zeit.cms.content.contentsource.FolderSource()
    expected_types = ['collection']

    copy_inherited_functions(ContentSourceBase, locals())
