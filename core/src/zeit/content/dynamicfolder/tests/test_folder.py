# coding: utf-8
from unittest import mock
import importlib.resources

import jinja2
import lxml.etree
import transaction
import zope.component

from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.interfaces import IUUID
from zeit.cms.repository.unknown import PersistentUnknownResource
from zeit.cms.workflow.interfaces import IPublicationDependencies
from zeit.content.rawxml.rawxml import RawXML
import zeit.cms.repository.folder
import zeit.cms.testcontenttype.testcontenttype
import zeit.cms.testing
import zeit.content.cp.interfaces
import zeit.content.dynamicfolder.interfaces as DFinterfaces
import zeit.content.dynamicfolder.materialize
import zeit.content.dynamicfolder.testing


class TestContainerMethodsRespectVirtualChildren(
    zeit.content.dynamicfolder.testing.FunctionalTestCase
):
    """Test folder methods like keys, values etc to return virtual children."""

    def setUp(self):
        super().setUp()
        self.folder = self.repository['dynamicfolder']

    def assert_xanten_has_basic_info_set(self, xanten):
        self.assertEqual('xanten', xanten.__name__)
        self.assertEqual('Xanten', xanten.title)
        self.assertEqual('http://xml.zeit.de/dynamicfolder/xanten', xanten.uniqueId)

    def test_folder_keys_contains_children_defined_in_xml_config(self):
        self.assertEqual(
            ['art-déco', 'xaernten', 'xanten', 'xinjiang', 'überlingen'], sorted(iter(self.folder))
        )

    def test_folder_iter_contains_children_defined_in_xml_config(self):
        self.assertEqual(
            ['art-déco', 'xaernten', 'xanten', 'xinjiang', 'überlingen'], sorted(iter(self.folder))
        )

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
        self.assertEqual(5, len(self.folder))

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
        content = zeit.cms.testcontenttype.testcontenttype.ExampleContentType()
        content.title = 'FOO'
        self.folder['xanten'] = content
        self.assertEqual('FOO', self.folder['xanten'].title)

    def test_delete_materialized_content_goes_back_to_virtual(self):
        content = zeit.cms.testcontenttype.testcontenttype.ExampleContentType()
        self.folder['xanten'] = content
        del self.folder['xanten']
        self.assertIn('xanten', self.folder)

    def test_delete_on_virtual_child_does_nothing(self):
        del self.folder['xanten']
        self.assertIn('xanten', self.folder)


class TestDynamicFolder(zeit.content.dynamicfolder.testing.FunctionalTestCase):
    """Tests behaviour that exceeds basic container methods like keys, get etc."""

    def setUp(self):
        super().setUp()
        self.folder = self.repository['dynamicfolder']

    def test_checkin_virtual_content_materializes_it(self):
        self.assertEqual('Xanten', self.folder['xanten'].title)
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
        self.folder['foo'] = zeit.cms.testcontenttype.testcontenttype.ExampleContentType()
        self.assertIn('foo', self.folder)
        self.assertIn('xanten', self.folder)

    def test_deleting_manual_content_reveals_virtual_content_again(self):
        content = zeit.cms.testcontenttype.testcontenttype.ExampleContentType()
        content.title = 'FOO'

        self.folder['xanten'] = content
        self.assertEqual('FOO', self.folder['xanten'].title)

        del self.folder['xanten']
        self.assertEqual('Xanten', self.folder['xanten'].title)

    def test_fills_in_template_placeholders_from_config_entries(self):
        cp = self.folder['xanten']
        self.assertTrue(zeit.cms.repository.interfaces.IRepositoryContent.providedBy(cp))
        self.assertTrue(zeit.content.cp.interfaces.ICenterPage.providedBy(cp))
        self.assertTrue(zeit.content.cp.interfaces.ICP2015.providedBy(cp))
        self.assertEqual('Xanten', cp.title)

    def test_template_handles_umlauts_and_xml_special_chars(self):
        cp = self.folder['xaernten']
        self.assertEqual('Xärnten & mehr', cp.title)

    def test_text_of_tags_can_be_used_in_template(self):
        # Remove all virtual childs that have been cached
        self.repository._content.clear()

        with mock.patch('jinja2.Template.render') as render:
            render.return_value = ''
            self.folder['xinjiang']  # load files and renders template
            self.assertEqual(1, render.call_count)
            self.assertIn(('text', 'Text Xinjiang'), render.call_args[1].items())

    def test_parent_can_be_accessed_in_template(self):
        with mock.patch(
            'zeit.content.dynamicfolder.folder.RepositoryDynamicFolder.content_template',
            new_callable=mock.PropertyMock,
        ) as template:
            template.return_value = jinja2.Template(
                """
<test>
    <head />
    <body>{{url_value}} {{__parent__.__name__}}</body>
</test>"""
            )
            self.assertIn(
                '<body>xanten dynamicfolder</body>',
                lxml.etree.tostring(self.folder['xanten'].xml, encoding=str),
            )

    def test_works_with_raxml_template(self):
        # These get an xml declaration in their serialization, so we must not
        # process them as unicode, else lxml complains.
        with (
            importlib.resources.files(__package__) / 'fixtures/dynamic-centerpages/template.xml'
        ).open() as f:
            self.repository['data']['template.xml'] = RawXML(f)
        with self.assertNothingRaised():
            self.folder['xanten']

    def test_works_with_unknown_type_template(self):
        # These don't get an xml declaration in their serialization, but
        # luckily(?) lxml doesn't care if we use unicode or utf-8 in that case.
        self.repository['data']['template.xml'] = PersistentUnknownResource(
            data=(
                importlib.resources.files(__package__) / 'fixtures/dynamic-centerpages/template.xml'
            ).read_text('latin-1')
        )
        with self.assertNothingRaised():
            self.folder['xanten']

    def test_converts_xml_attribute_nodes_into_dav_properties(self):
        self.assertEqual('Deutschland', self.folder['xanten'].ressort)

    def test_does_not_copy_uuid_of_template_into_content(self):
        self.assertNotEqual(
            '{urn:uuid:6a5bcb2a-bd80-499b-ad79-72eb0a07e65e}', IUUID(self.folder['xanten']).id
        )

    def test_calculates_uuid_from_uniqueid(self):
        second = zeit.content.dynamicfolder.folder.RepositoryDynamicFolder()
        second.config_file = self.repository['data']['config.xml']
        self.repository['secondfolder'] = second
        transaction.commit()
        self.assertNotEqual(IUUID(self.folder['xanten']).id, IUUID(second['xanten']).id)

    def test_checkout_preserves_dav_properties_from_xml(self):
        # We need a DAV property that is handled by a separate adapter to see
        # the effect, since direct DAV properties are directly copied to XML,
        # so for those it makes no difference if e.g. VirtualProperties were
        # still used for checked-out IVirtualContent, which they should not be.
        self.assertEqual('seo-title', zeit.seo.interfaces.ISEO(self.folder['xanten']).html_title)
        with checked_out(self.folder['xanten']) as co:
            self.assertEqual('seo-title', zeit.seo.interfaces.ISEO(co).html_title)
            zeit.seo.interfaces.ISEO(co).html_title = 'changed'
        self.assertEqual('changed', zeit.seo.interfaces.ISEO(self.folder['xanten']).html_title)

    def test_does_not_break_on_erroneous_config(self):
        from zeit.content.dynamicfolder.folder import RepositoryDynamicFolder

        dynamic = RepositoryDynamicFolder()
        dynamic.config_file = self.repository['data']['template.xml']
        self.repository['brokenfolder'] = dynamic
        transaction.commit()
        with self.assertNothingRaised():
            self.repository['brokenfolder'].values()

    def test_publish_dynamic_folder_does_not_publish_contents(self):
        calls = []

        def check_publish(context, event):
            calls.append(context.uniqueId)

        zope.component.getGlobalSiteManager().registerHandler(
            check_publish,
            (
                zeit.cms.repository.interfaces.IRepositoryContent,
                zeit.cms.workflow.interfaces.IPublishedEvent,
            ),
        )
        zeit.cms.workflow.interfaces.IPublish(self.folder).publish(background=False)
        self.assertIn('http://xml.zeit.de/dynamicfolder', calls)
        # Would be nice to check these, for completeness, but mock IPublish
        # does not handle IPublicationDependencies, so we have
        # `test_publishes_folder_with_config_and_template` instead.
        # | self.assertIn('http://xml.zeit.de/data/config.xml', calls)
        # | self.assertIn('http://xml.zeit.de/data/template.xml', calls)
        self.assertNotIn('http://xml.zeit.de/dynamicfolder/art-déco', calls)
        self.assertNotIn('http://xml.zeit.de/dynamicfolder/xaernten', calls)
        self.assertNotIn('http://xml.zeit.de/dynamicfolder/xanten', calls)
        self.assertNotIn('http://xml.zeit.de/dynamicfolder/xinjiang', calls)
        self.assertNotIn('http://xml.zeit.de/dynamicfolder/überlingen', calls)

    def test_publishes_folder_with_config_and_template(self):
        pub = IPublicationDependencies(self.folder)
        for deps in [pub.get_dependencies(), pub.get_retract_dependencies()]:
            self.assertIn(self.folder.config_file, deps)
            self.assertIn(self.folder.content_template_file, deps)


class MaterializeDynamicFolder(zeit.cms.testing.FunctionalTestCase):
    layer = zeit.content.dynamicfolder.testing.DynamicLayer(
        path='tests/fixtures/dynamic-articles/', files=['config.xml', 'template.xml']
    )

    def setUp(self):
        super().setUp()
        self.folder = self.repository['dynamicfolder']

    def test_checkin_materialized_content_preserves_materialization(self):
        zeit.content.dynamicfolder.materialize.materialize_content(self.folder)
        transaction.commit()
        self.assertEqual(
            'Wahlergebnis in Kiel', self.folder['wahlergebnis-kiel-wahlkreis-5-live'].title
        )
        with checked_out(self.folder['wahlergebnis-kiel-wahlkreis-5-live']) as co:
            co.title = 'foo'
        self.assertEqual('foo', self.folder['wahlergebnis-kiel-wahlkreis-5-live'].title)
        self.assertTrue(
            DFinterfaces.IMaterializedContent.providedBy(
                self.folder['wahlergebnis-kiel-wahlkreis-5-live']
            )
        )

    def test_materializing_virtual_content(self):
        zeit.content.dynamicfolder.materialize.materialize_content(self.folder)
        transaction.commit()
        self.assertFalse(
            DFinterfaces.IVirtualContent.providedBy(
                self.folder['wahlergebnis-kiel-wahlkreis-5-live']
            )
        )
        self.assertTrue(
            DFinterfaces.IMaterializedContent.providedBy(
                self.folder['wahlergebnis-kiel-wahlkreis-5-live']
            )
        )

    def test_materialized_content_is_virtual_content_again(self):
        zeit.content.dynamicfolder.materialize.materialize_content(self.folder)
        transaction.commit()
        del self.folder['wahlergebnis-kiel-wahlkreis-5-live']
        self.assertIn('wahlergebnis-kiel-wahlkreis-5-live', self.folder)
        self.assertTrue(
            DFinterfaces.IVirtualContent.providedBy(
                self.folder['wahlergebnis-kiel-wahlkreis-5-live']
            )
        )

    def test_publish_materialized_content(self):
        zeit.content.dynamicfolder.materialize.materialize_content(self.folder)
        zeit.content.dynamicfolder.materialize.publish_content(self.folder)
        self.assertTrue(
            zeit.cms.workflow.interfaces.IPublishInfo(
                self.folder['wahlergebnis-kiel-wahlkreis-5-live']
            ).published
        )

    def test_folder_should_not_be_materialized_content(self):
        """
        And therefore is never published, when
        zeit.content.dynamicfolder.publish.publish_content is called
        """
        self.repository['dynamicfolder']['real-folder'] = zeit.cms.repository.folder.Folder()
        zeit.content.dynamicfolder.materialize.materialize_content(self.repository['dynamicfolder'])
        transaction.commit()
        self.assertFalse(
            DFinterfaces.IVirtualContent.providedBy(self.repository['dynamicfolder']['real-folder'])
        )

    def test_materialized_content_is_updated_when_materialized_again(self):
        zeit.content.dynamicfolder.materialize.materialize_content(self.folder)
        transaction.commit()
        with checked_out(self.folder['wahlergebnis-kiel-wahlkreis-5-live']) as co:
            co.title = 'foo'
        self.assertEqual('foo', self.folder['wahlergebnis-kiel-wahlkreis-5-live'].title)
        zeit.content.dynamicfolder.materialize.materialize_content(self.folder)
        transaction.commit()
        self.assertEqual(
            'Wahlergebnis in Kiel', self.folder['wahlergebnis-kiel-wahlkreis-5-live'].title
        )
        self.assertTrue(
            DFinterfaces.IMaterializedContent.providedBy(
                self.folder['wahlergebnis-kiel-wahlkreis-5-live']
            )
        )

    def test_remove_config_file_does_not_break_dynamic_folder(self):
        self.repository['dynamicfolder']['config.xml'] = self.repository['data']['config.xml']
        with checked_out(self.folder) as co:
            co.config_file = self.repository['dynamicfolder']['config.xml']
        zeit.content.dynamicfolder.materialize.materialize_content(self.folder)
        del self.repository['dynamicfolder']['config.xml']
        transaction.commit()
        [i for i in self.folder.values()]  # does not raise RecursionError
