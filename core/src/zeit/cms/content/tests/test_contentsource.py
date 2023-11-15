from zeit.cms.testing import copy_inherited_functions
import zeit.cms.testing
import zeit.cms.content.contentsource


class ContentSourceBase:
    source = zeit.cms.content.contentsource.CMSContentSource()
    expected_types = ['channel', 'collection', 'file', 'testcontenttype', 'unknown']

    def test_get_check_types(self):
        self.assertEqual(self.expected_types, sorted(self.source.get_check_types()))


class FolderSourceTest(ContentSourceBase, zeit.cms.testing.ZeitCmsTestCase):
    source = zeit.cms.content.contentsource.FolderSource()
    expected_types = ['collection']

    copy_inherited_functions(ContentSourceBase, locals())
