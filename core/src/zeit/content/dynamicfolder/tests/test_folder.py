# coding: utf-8
from zeit.cms.checkout.helper import checked_out
from zeit.cms.repository.unknown import PersistentUnknownResource
from zeit.content.rawxml.rawxml import RawXML
import mock
import pkg_resources
import transaction
import zeit.cms.testcontenttype.testcontenttype
import zeit.content.cp.interfaces
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
        self.assertEqual(
            [u'art-déco', 'xaernten', 'xanten', 'xinjiang'],
            sorted(list(iter(self.folder))))

    def test_folder_iter_contains_children_defined_in_xml_config(self):
        self.assertEqual(
            [u'art-déco', 'xaernten', 'xanten', 'xinjiang'],
            sorted(list(iter(self.folder))))

    def test_folder_getitem_returns_child_with_basic_info_set(self):
        child = self.folder['xanten']
        self.assert_xanten_has_basic_info_set(child)

    def test_folder_get_returns_child_with_basic_info_set(self):
        child = self.folder.get('xanten')
        self.assert_xanten_has_basic_info_set(child)

    def test_folder_values_returns_childs_with_basic_info_set(self):
        for child in self.folder.values():
            if child.__name__ == 'xanten':
                self.assert_xanten_has_basic_info_set(child)
                break
        else:
            self.fail('Entry xanten not found.')

    def test_folder_len_counts_children_defined_in_xml_config(self):
        self.assertEqual(4, len(self.folder))

    def test_folder_items_returns_childs_with_basic_info_set(self):
        for key, value in self.folder.items():
            if key == 'xanten':
                self.assert_xanten_has_basic_info_set(value)
                break
        else:
            self.fail('Entry xanten not found.')

    def test_folder_contains_children_defined_in_xml_config(self):
        self.assertIn('xanten', self.folder)

    def test_setting_content_at_key_of_virtual_child_overwrites_it(self):
        content = zeit.cms.testcontenttype.testcontenttype.TestContentType()
        content.title = 'FOO'
        self.folder['xanten'] = content
        self.assertEqual('FOO', self.folder['xanten'].title)

    def test_delete_materialized_content_goes_back_to_virtual(self):
        content = zeit.cms.testcontenttype.testcontenttype.TestContentType()
        self.folder['xanten'] = content
        del self.folder['xanten']
        self.assertIn('xanten', self.folder)

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

    def test_checkin_virtual_content_materializes_it(self):
        # Fill cached values, since they must not interfere with ZODB/pickling.
        self.folder.cp_template
        self.folder.virtual_content

        self.assertEqual('Xanten', self.folder['xanten'].title)
        with mock.patch('zeit.find.search.search'):
            with checked_out(self.folder['xanten']) as co:
                co.title = 'foo'
            self.assertEqual('foo', self.folder['xanten'].title)

    def test_unconfigured_folder_does_not_break_due_to_missing_config(self):
        from ..folder import RepositoryDynamicFolder
        self.repository['folder'] = RepositoryDynamicFolder()
        self.assertEqual([], self.repository['folder'].items())

    def test_getitem_for_key_with_no_virtual_child_raises_KeyError(self):
        with self.assertRaises(KeyError):
            self.folder['Buxtehude']

    def test_folder_can_also_contain_normal_content(self):
        self.folder['foo'] = (
            zeit.cms.testcontenttype.testcontenttype.TestContentType())
        self.assertIn('foo', self.folder)
        self.assertIn('xanten', self.folder)

    def test_deleting_manual_content_reveals_virtual_content_again(self):
        content = zeit.cms.testcontenttype.testcontenttype.TestContentType()
        content.title = 'FOO'

        self.folder['xanten'] = content
        self.assertEqual('FOO', self.folder['xanten'].title)

        del self.folder['xanten']
        self.assertEqual('Xanten', self.folder['xanten'].title)

    def test_fills_in_template_placeholders_from_config_entries(self):
        cp = self.folder['xanten']
        self.assertTrue(zeit.content.cp.interfaces.ICenterPage.providedBy(cp))
        self.assertTrue(zeit.content.cp.interfaces.ICP2015.providedBy(cp))
        self.assertEqual('Xanten', cp.title)

    def test_template_handles_umlauts_and_xml_special_chars(self):
        cp = self.folder['xaernten']
        self.assertEqual(u'Xärnten & mehr', cp.title)

    def test_text_of_tags_can_be_used_in_template(self):
        # Remove all virtual childs that have been cached
        self.repository.uncontained_content = {}

        with mock.patch('jinja2.Template.render') as render:
            render.return_value = u''
            self.folder['xinjiang']  # load files and renders template
            self.assertEqual(1, render.call_count)
            self.assertIn(
                ('text', 'Text Xinjiang'), render.call_args[1].items())

    def test_works_with_raxml_template(self):
        # These get an xml declaration in their serialization, so we must not
        # process them as unicode, else lxml complains.
        transaction.abort()  # Clear Repository child cache
        self.repository['data']['template.xml'] = RawXML(
            pkg_resources.resource_stream(__name__, 'fixtures/template.xml'))
        with self.assertNothingRaised():
            self.folder['xanten']

    def test_works_with_unknown_type_template(self):
        # These don't get an xml declaration in their serialization, but
        # luckily(?) lxml doesn't care if we use unicode or utf-8 in that case.
        transaction.abort()  # Clear Repository child cache
        self.repository['data']['template.xml'] = PersistentUnknownResource(
            data=pkg_resources.resource_string(
                __name__, 'fixtures/template.xml').decode('latin-1'))
        with self.assertNothingRaised():
            self.folder['xanten']

    def test_converts_xml_attribute_nodes_into_dav_properties(self):
        self.assertEqual('Deutschland', self.folder['xanten'].ressort)

    def assert_published(self, content):
        info = zeit.cms.workflow.interfaces.IPublishInfo(content)
        self.assertTrue(info.published, '%s not published' % content.uniqueId)

    def test_publishes_folder_with_config_and_template(self):
        transaction.commit()  # XXX Work around remotetask / zodb weirdness
        zeit.cms.workflow.interfaces.IPublish(self.folder).publish()
        zeit.workflow.testing.run_publish()
        self.assert_published(self.folder)
        self.assert_published(self.folder.config_file)
        self.assert_published(self.folder.content_template_file)
