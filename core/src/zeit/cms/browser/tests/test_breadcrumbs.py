# coding: utf8
from unittest import mock

import zope.publisher.browser

import zeit.cms.browser.breadcrumbs
import zeit.cms.checkout.interfaces
import zeit.cms.repository.folder
import zeit.cms.repository.interfaces
import zeit.cms.testcontenttype.testcontenttype
import zeit.cms.testing
import zeit.cms.workingcopy.interfaces


class BreadcrumbsView(zeit.cms.browser.breadcrumbs.Breadcrumbs):
    def __init__(self, context):
        super().__init__()
        self.context = context
        self.request = zope.publisher.browser.TestRequest()


class Breadcrumbs(zeit.cms.testing.ZeitCmsTestCase):
    def setUp(self):
        super().setUp()
        kultur = self.repository['kultur'] = zeit.cms.repository.folder.Folder()
        kultur['musik'] = zeit.cms.repository.folder.Folder()

    def test_icommonmetadata_lists_ressort_and_sub_ressort(self):
        content = zeit.cms.testcontenttype.testcontenttype.ExampleContentType()
        self.repository['foo'] = content
        content.ressort = 'Kultur'
        content.sub_ressort = 'Musik'
        self.assertEqual(
            [
                {'title': 'Kultur', 'uniqueId': None, 'url': 'http://127.0.0.1/repository/kultur'},
                {
                    'title': 'Musik',
                    'uniqueId': None,
                    'url': 'http://127.0.0.1/repository/kultur/musik',
                },
                {
                    'title': 'foo',
                    'uniqueId': 'http://xml.zeit.de/foo',
                    'url': 'http://127.0.0.1/repository/foo',
                },
            ],
            BreadcrumbsView(content).get_breadcrumbs,
        )

    def test_icommonmetadata_without_ressort_omits_item(self):
        content = zeit.cms.testcontenttype.testcontenttype.ExampleContentType()
        self.repository['foo'] = content
        self.assertEqual(
            [
                {
                    'title': 'foo',
                    'uniqueId': 'http://xml.zeit.de/foo',
                    'url': 'http://127.0.0.1/repository/foo',
                },
            ],
            BreadcrumbsView(content).get_breadcrumbs,
        )

    def test_icommonmetadata_without_sub_ressort_omits_item(self):
        content = zeit.cms.testcontenttype.testcontenttype.ExampleContentType()
        self.repository['foo'] = content
        content.ressort = 'Kultur'
        self.assertEqual(
            [
                {'title': 'Kultur', 'uniqueId': None, 'url': 'http://127.0.0.1/repository/kultur'},
                {
                    'title': 'foo',
                    'uniqueId': 'http://xml.zeit.de/foo',
                    'url': 'http://127.0.0.1/repository/foo',
                },
            ],
            BreadcrumbsView(content).get_breadcrumbs,
        )

    def test_icommonmetadata_with_invalid_ressort_omits_item(self):
        content = zeit.cms.testcontenttype.testcontenttype.ExampleContentType()
        self.repository['foo'] = content
        content.ressort = 'Kültür'
        self.assertEqual(
            [
                {
                    'title': 'foo',
                    'uniqueId': 'http://xml.zeit.de/foo',
                    'url': 'http://127.0.0.1/repository/foo',
                },
            ],
            BreadcrumbsView(content).get_breadcrumbs,
        )

    def test_no_icommonmetadata_lists_repo_path(self):
        content = self.repository['kultur']['musik']
        self.assertEqual(
            [
                {
                    'title': 'repository',
                    'uniqueId': 'http://xml.zeit.de/',
                    'url': 'http://127.0.0.1/repository',
                },
                {
                    'title': 'kultur',
                    'uniqueId': 'http://xml.zeit.de/kultur',
                    'url': 'http://127.0.0.1/repository/kultur',
                },
                {
                    'title': 'musik',
                    'uniqueId': 'http://xml.zeit.de/kultur/musik',
                    'url': 'http://127.0.0.1/repository/kultur/musik',
                },
            ],
            BreadcrumbsView(content).get_breadcrumbs,
        )

    def test_no_icommonmetadata_in_wc_lists_repo_path(self):
        self.repository['kultur']['file'] = zeit.cms.repository.file.LocalFile()
        content = self.repository['kultur']['file']
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(content)
        co = manager.checkout()
        self.assertEqual(
            [
                {
                    'title': 'repository',
                    'uniqueId': 'http://xml.zeit.de/',
                    'url': 'http://127.0.0.1/repository',
                },
                {
                    'title': 'kultur',
                    'uniqueId': 'http://xml.zeit.de/kultur',
                    'url': 'http://127.0.0.1/repository/kultur',
                },
                {
                    'title': 'file',
                    'uniqueId': 'http://xml.zeit.de/kultur/file',
                    'url': 'http://127.0.0.1/repository/kultur/file',
                },
            ],
            BreadcrumbsView(co).get_breadcrumbs,
        )

    def test_breadcrumbs_work_for_non_content_object(self):
        obj = zeit.cms.workingcopy.interfaces.IWorkingcopy(None)
        self.assertEqual(
            [
                {'title': 'workingcopy', 'uniqueId': None, 'url': 'http://127.0.0.1/workingcopy'},
                {
                    'title': 'zope.user',
                    'uniqueId': None,
                    'url': 'http://127.0.0.1/workingcopy/zope.user',
                },
            ],
            BreadcrumbsView(obj).get_breadcrumbs,
        )

    def test_local_content_without_corr_repo_content_lists_name(self):
        self.repository['kultur']['file'] = zeit.cms.repository.file.LocalFile()
        content = self.repository['kultur']['file']
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(content)
        co = manager.checkout()
        del self.repository['kultur']['file']
        self.assertEqual(
            [
                {
                    'title': 'file',
                    'uniqueId': 'http://xml.zeit.de/kultur/file',
                    'url': 'http://127.0.0.1/workingcopy/zope.user/file',
                },
            ],
            BreadcrumbsView(co).get_breadcrumbs,
        )

    def test_temporary_document_name_is_abbreviated_as_new(self):
        content = zeit.cms.testcontenttype.testcontenttype.ExampleContentType()
        self.repository['foo'] = content
        zeit.cms.repository.interfaces.IAutomaticallyRenameable(content).renameable = True
        self.assertEqual(
            [
                {
                    'title': '(new)',
                    'uniqueId': 'http://xml.zeit.de/foo',
                    'url': 'http://127.0.0.1/repository/foo',
                },
            ],
            BreadcrumbsView(content).get_breadcrumbs,
        )

    def test_deconfigured_should_use_from_path_only(self):
        import zope.app.appsetup.product

        zope.app.appsetup.product._configs['zeit.cms']['breadcrumbs-use-common-metadata'] = 'false'
        content = zeit.cms.testcontenttype.testcontenttype.ExampleContentType()
        self.repository['foo'] = content
        view = BreadcrumbsView(content)
        view.get_breadcrumbs_from_path = mock.Mock()
        view.get_breadcrumbs  # noqa: B018
        self.assertTrue(view.get_breadcrumbs_from_path.called)

    def test_missing_option_should_use_from_path_only(self):
        import zope.app.appsetup.product

        del zope.app.appsetup.product._configs['zeit.cms']['breadcrumbs-use-common-metadata']
        content = zeit.cms.testcontenttype.testcontenttype.ExampleContentType()
        self.repository['foo'] = content
        view = BreadcrumbsView(content)
        view.get_breadcrumbs_from_path = mock.Mock()
        view.get_breadcrumbs  # noqa: B018
        self.assertTrue(view.get_breadcrumbs_from_path.called)

    def test_missing_config_should_use_from_path_only(self):
        # This makes testing easier
        import zope.app.appsetup.product

        del zope.app.appsetup.product._configs['zeit.cms']['breadcrumbs-use-common-metadata']
        content = zeit.cms.testcontenttype.testcontenttype.ExampleContentType()
        self.repository['foo'] = content
        view = BreadcrumbsView(content)
        view.get_breadcrumbs_from_path = mock.Mock()
        view.get_breadcrumbs  # noqa: B018
        self.assertTrue(view.get_breadcrumbs_from_path.called)

    def test_deconfigured_no_icommonmetadata_in_wc_lists_wc_path(self):
        self.repository['kultur']['file'] = zeit.cms.repository.file.LocalFile()
        content = self.repository['kultur']['file']
        zope.app.appsetup.product._configs['zeit.cms']['breadcrumbs-use-common-metadata'] = 'false'
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(content)
        co = manager.checkout()
        self.maxDiff = None
        self.assertEqual(
            [
                {'title': 'workingcopy', 'uniqueId': None, 'url': 'http://127.0.0.1/workingcopy'},
                {
                    'title': 'zope.user',
                    'uniqueId': None,
                    'url': 'http://127.0.0.1/workingcopy/zope.user',
                },
                {
                    'title': 'file',
                    'uniqueId': 'http://xml.zeit.de/kultur/file',
                    'url': 'http://127.0.0.1/workingcopy/zope.user/file',
                },
            ],
            BreadcrumbsView(co).get_breadcrumbs,
        )
