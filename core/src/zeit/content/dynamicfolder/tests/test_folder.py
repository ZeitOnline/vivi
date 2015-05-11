import unittest
import zeit.cms.testcontenttype.testcontenttype
import zeit.content.dynamicfolder.testing


class TestContainerMethodsRespectVirtualChildren(
        zeit.content.dynamicfolder.testing.FunctionalTestCase):
    """Test folder methods like keys, values etc to return virtual children."""

    def setUp(self):
        super(TestContainerMethodsRespectVirtualChildren, self).setUp()
        self.folder = self.repository['dynamicfolder']

    def assert_xanten_has_basic_info_set(self, xanten):
        self.assertEqual('xanten', xanten.__name__)
        self.assertEqual('Xanten', xanten.title)
        self.assertEqual(
            'http://xml.zeit.de/dynamicfolder/xanten', xanten.uniqueId)

    def test_folder_keys_contains_children_defined_in_xml_config(self):
        self.assertEqual(['xanten', 'xinjiang'], list(self.folder.keys()))

    def test_folder_iter_contains_children_defined_in_xml_config(self):
        self.assertEqual(['xanten', 'xinjiang'], list(iter(self.folder)))

    def test_folder_getitem_returns_child_with_basic_info_set(self):
        child = self.folder['xanten']
        self.assert_xanten_has_basic_info_set(child)

    def test_folder_get_returns_child_with_basic_info_set(self):
        child = self.folder.get('xanten')
        self.assert_xanten_has_basic_info_set(child)

    def test_folder_values_returns_childs_with_basic_info_set(self):
        children = list(self.folder.values())
        self.assert_xanten_has_basic_info_set(children[0])

    def test_folder_len_counts_children_defined_in_xml_config(self):
        self.assertEqual(2, len(self.folder))

    def test_folder_items_returns_childs_with_basic_info_set(self):
        items = list(self.folder.items())
        key, value = items[0]
        self.assertEqual('xanten', key)
        self.assert_xanten_has_basic_info_set(value)

    def test_folder_contains_children_defined_in_xml_config(self):
        self.assertIn('xanten', self.folder)

    @unittest.expectedFailure
    def test_setting_content_at_key_of_virtual_child_overwrites_it(self):
        content = zeit.cms.testcontenttype.testcontenttype.TestContentType()
        content.title = 'FOO'
        self.folder['xanten'] = content
        self.assertEqual('FOO', self.folder['xanten'].title)

    @unittest.expectedFailure
    def test_delete_on_virtual_child_does_nothing(self):
        del self.folder['xanten']
        self.assertIn('xanten', self.folder)


class TestDynamicFolder(
        zeit.content.dynamicfolder.testing.FunctionalTestCase):
    """Tests behaviour that exceeds basic container methods like keys, get etc.
    """

    def setUp(self):
        super(TestDynamicFolder, self).setUp()
        self.folder = self.repository['dynamicfolder']

    def test_folder_can_also_contain_normal_content(self):
        self.folder['foo'] = (
            zeit.cms.testcontenttype.testcontenttype.TestContentType())
        self.assertEqual(3, len(self.folder))
        self.assertEqual(['foo', 'xanten', 'xinjiang'], list(self.folder))

    @unittest.expectedFailure
    def test_deleting_manual_content_reveals_virtual_content_again(self):
        content = zeit.cms.testcontenttype.testcontenttype.TestContentType()
        content.title = 'FOO'

        self.folder['xanten'] = content
        self.assertEqual('FOO', self.folder['xanten'].title)

        del self.folder['xanten']
        self.assertEqual('Xanten', self.folder['xanten'].title)
