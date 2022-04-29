from unittest import mock
from zeit.cms.interfaces import ICMSContent
from zeit.cms.repository.repository import live_url_to_content
from zeit.cms.repository.repository import live_https_url_to_content
from zeit.cms.repository.repository import vivi_url_to_content
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import gocept.testing.mock
import unittest
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.cms.workingcopy.interfaces
import zope.component
import zope.security.management


class TestConflicts(zeit.cms.testing.ZeitCmsTestCase):

    def setUp(self):
        super(TestConflicts, self).setUp()
        self.repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        self.repository['online']['conflicting'] = (
            zeit.cms.repository.unknown.PersistentUnknownResource('Pop'))
        self.res = zeit.cms.workingcopy.interfaces.ILocalContent(
            self.repository['online']['conflicting'])
        self.repository['online']['conflicting'] = (
            zeit.cms.repository.unknown.PersistentUnknownResource('Bang'))

    def test_conflict_on_setitem(self):
        self.assertRaises(
            zeit.cms.repository.interfaces.ConflictError,
            self.repository['online'].__setitem__, 'conflicting', self.res)

    def test_conflict_on_add_content(self):
        self.assertRaises(
            zeit.cms.repository.interfaces.ConflictError,
            self.repository.addContent, self.res)

    def test_conflict_override(self):
        self.repository.addContent(self.res, ignore_conflicts=True)
        self.assertEqual('Pop',
                         self.repository['online']['conflicting'].data)


class LiveURLToContent(unittest.TestCase):

    def setUp(self):
        self.patches = gocept.testing.mock.Patches()
        self.cmscontent = self.patches.add('zeit.cms.interfaces.ICMSContent')

    def tearDown(self):
        self.patches.reset()

    def test_www_host_is_replaced_by_xml_host(self):
        live_url_to_content('http://www.foo.bar/test')
        self.cmscontent.assert_called_with('http://xml.foo.bar/test', None)

    def test_www_in_path_is_left_alone(self):
        live_url_to_content('http://www.foo.bar/www/test')
        self.cmscontent.assert_called_with('http://xml.foo.bar/www/test', None)

    def test_page_marker_is_chopped_off(self):
        live_url_to_content(
            'http://www.zeit.de/online/2007/01/Somalia/seite-5')
        self.cmscontent.assert_called_with(
            'http://xml.zeit.de/online/2007/01/Somalia', None)

    def test_komplettansicht_is_chopped_off(self):
        live_url_to_content(
            'http://www.zeit.de/online/2007/01/Somalia/komplettansicht')
        self.cmscontent.assert_called_with(
            'http://xml.zeit.de/online/2007/01/Somalia', None)

    def test_ssl_is_replaced_by_xml(self):
        live_https_url_to_content('https://www.foo.bar/test')
        self.cmscontent.assert_called_with('http://xml.foo.bar/test', None)


class ViviURLToContent(unittest.TestCase):

    def setUp(self):
        self.patches = gocept.testing.mock.Patches()
        self.cmscontent = self.patches.add('zeit.cms.interfaces.ICMSContent')

    def tearDown(self):
        self.patches.reset()

    def test_vivi_url_is_replaced_by_xml_url(self):
        vivi_url_to_content('http://vivi.zeit.de/repository/2007/politik')
        self.cmscontent.assert_called_with(
            'http://xml.zeit.de/2007/politik', None)

    def test_vivi_view_names_are_removed(self):
        vivi_url_to_content(
            'http://vivi.zeit.de/repository/2007/politik/@@something.html')
        self.cmscontent.assert_called_with(
            'http://xml.zeit.de/2007/politik', None)

    def test_url_not_in_repository_returns_none(self):
        self.assertIsNone(
            vivi_url_to_content(
                'http://vivi.zeit.de/workingcopy/user/Somalia'))
        self.assertFalse(self.cmscontent.called)


class UniqueIdToContentIntegration(zeit.cms.testing.ZeitCmsTestCase):

    def test_xml_zeit_de_is_translated_to_content_object(self):
        self.assertIsInstance(
            ICMSContent('http://xml.zeit.de/testcontent'), ExampleContentType)

    def test_www_zeit_de_is_wired_up_and_delegates_to_xml_zeit_de(self):
        self.assertEqual(
            ICMSContent('http://xml.zeit.de/testcontent'),
            ICMSContent('http://www.zeit.de/testcontent'))

    def test_ssl_www_zeit_de_is_wired_up_and_delegates_to_xml_zeit_de(self):
        self.assertEqual(
            ICMSContent('http://xml.zeit.de/testcontent'),
            ICMSContent('https://www.zeit.de/testcontent'))

    def test_www_zeit_de_does_not_raise_if_content_not_exists(self):
        live_url_to_content('http://www.zeit.de/foo/bar/foobaz')

    def test_vivi_zeit_de_is_wired_up_and_delegates_to_xml_zeit_de(self):
        self.assertEqual(
            ICMSContent('http://xml.zeit.de/testcontent'),
            ICMSContent('http://vivi.zeit.de/repository/testcontent'))

    def test_ssl_vivi_zeit_de_is_wired_up_and_delegates_to_xml_zeit_de(self):
        self.assertEqual(
            ICMSContent('http://xml.zeit.de/testcontent'),
            ICMSContent('https://vivi.zeit.de/repository/testcontent'))

    def test_vivi_zeit_de_does_not_raise_if_content_not_exists(self):
        vivi_url_to_content('http://vivi.zeit.de/repository/foo/bar/foobaz')

    def test_no_interaction_ignores_workingcopy(self):
        zope.security.management.endInteraction()
        self.assertEqual(
            ICMSContent('http://xml.zeit.de/testcontent'),
            zeit.cms.cmscontent.resolve_wc_or_repository(
                'http://xml.zeit.de/testcontent'))


class RepositoryTest(zeit.cms.testing.ZeitCmsTestCase):

    def test_inconsistent_child_names_do_not_yields_non_existing_objects(self):
        self.repository['cache'] = zeit.cms.repository.folder.Folder()
        folder = self.repository['cache']
        folder['one'] = ExampleContentType()
        with mock.patch('zeit.connector.mock.Connector.listCollection') as lst:
            lst.return_value = [
                ('one', 'http://xml.zeit.de/cache/one'),
                ('two', 'http://xml.zeit.de/cache/two')]
            self.assertEqual(['one', 'two'], list(folder.keys()))
            self.assertEqual(
                ['http://xml.zeit.de/cache/one'],
                [x.uniqueId for x in folder.values()])


class ContentBaseTest(zeit.cms.testing.ZeitCmsTestCase):

    def test_implements_IRepositoryContent(self):
        self.assertTrue(
            zeit.cms.repository.interfaces.IRepositoryContent.providedBy(
                self.repository.getContent('http://xml.zeit.de/testcontent')))

    def test_has_parent(self):
        self.assertEqual(
            self.repository['online']['2007']['01'],
            self.repository.getContent(
                'http://xml.zeit.de/online/2007/01/Somalia').__parent__)

    def test_root_folder_is_repository(self):
        self.assertEqual(
            self.repository,
            self.repository.getContent(
                'http://xml.zeit.de/testcontent').__parent__)

    def test_result_has_name(self):
        self.assertEqual(
            'testcontent',
            self.repository.getContent(
                'http://xml.zeit.de/testcontent').__name__)

    def test_can_write_explicit_parent(self):
        one = zeit.cms.repository.repository.ContentBase()
        one.__parent__ = 'foo'
        self.assertEqual(one.__parent__, 'foo')

    def test_can_write_none_to_parent(self):
        one = zeit.cms.repository.repository.ContentBase()
        one.__parent__ = None
        self.assertIsNone(one.__parent__)
