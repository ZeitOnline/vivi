# coding: utf-8
# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import zeit.cms.browser.breadcrumbs
import zeit.cms.checkout.interfaces
import zeit.cms.repository.file
import zeit.cms.repository.folder
import zeit.cms.testcontenttype.testcontenttype
import zeit.cms.testing
import zeit.cms.workingcopy.interfaces
import zope.publisher.browser


class BreadcrumbsView(zeit.cms.browser.breadcrumbs.Breadcrumbs):

    def __init__(self, context):
        super(BreadcrumbsView, self).__init__()
        self.context = context
        self.request = zope.publisher.browser.TestRequest()


class Breadcrumbs(zeit.cms.testing.FunctionalTestCase):

    def setUp(self):
        super(Breadcrumbs, self).setUp()
        kultur = self.repository['kultur'] = \
            zeit.cms.repository.folder.Folder()
        kultur['musik'] = zeit.cms.repository.folder.Folder()

    def test_icommonmetadata_lists_ressort_and_sub_ressort(self):
        content = zeit.cms.testcontenttype.testcontenttype.TestContentType()
        self.repository['foo'] = content
        content.ressort = u'Kultur'
        content.sub_ressort = u'Musik'
        self.assertEqual([
                dict(title=u'Kultur',
                     uniqueId=None,
                     url='http://127.0.0.1/repository/kultur',
                    ),
                dict(title=u'Musik',
                     uniqueId=None,
                     url='http://127.0.0.1/repository/kultur/musik',
                    ),
                dict(title='foo',
                     uniqueId=u'http://xml.zeit.de/foo',
                     url='http://127.0.0.1/repository/foo',
                    ),
                ], BreadcrumbsView(content).get_breadcrumbs)

    def test_icommonmetadata_without_ressort_omits_item(self):
        content = zeit.cms.testcontenttype.testcontenttype.TestContentType()
        self.repository['foo'] = content
        self.assertEqual([
                dict(title='foo',
                     uniqueId=u'http://xml.zeit.de/foo',
                     url='http://127.0.0.1/repository/foo',
                    ),
                ], BreadcrumbsView(content).get_breadcrumbs)

    def test_icommonmetadata_without_sub_ressort_omits_item(self):
        content = zeit.cms.testcontenttype.testcontenttype.TestContentType()
        self.repository['foo'] = content
        content.ressort = u'Kultur'
        self.assertEqual([
                dict(title=u'Kultur',
                     uniqueId=None,
                     url='http://127.0.0.1/repository/kultur',
                    ),
                dict(title='foo',
                     uniqueId=u'http://xml.zeit.de/foo',
                     url='http://127.0.0.1/repository/foo',
                    ),
                ], BreadcrumbsView(content).get_breadcrumbs)

    def test_icommonmetadata_with_invalid_ressort_omits_item(self):
        content = zeit.cms.testcontenttype.testcontenttype.TestContentType()
        self.repository['foo'] = content
        content.ressort = u'Kültür'
        self.assertEqual([
                dict(title='foo',
                     uniqueId=u'http://xml.zeit.de/foo',
                     url='http://127.0.0.1/repository/foo',
                    ),
                ], BreadcrumbsView(content).get_breadcrumbs)

    def test_no_icommonmetadata_lists_repo_path(self):
        content = self.repository['kultur']['musik']
        self.assertEqual([
                dict(title=u'repository',
                     uniqueId='http://xml.zeit.de/',
                     url='http://127.0.0.1/repository',
                    ),
                dict(title=u'kultur',
                     uniqueId='http://xml.zeit.de/kultur',
                     url='http://127.0.0.1/repository/kultur',
                    ),
                dict(title=u'musik',
                     uniqueId=u'http://xml.zeit.de/kultur/musik',
                     url='http://127.0.0.1/repository/kultur/musik',
                    ),
                ], BreadcrumbsView(content).get_breadcrumbs)

    def test_no_icommonmetadata_in_wc_lists_repo_path(self):
        content = self.repository['2006']['DSC00109_2.JPG']
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(content)
        co = manager.checkout()
        self.assertEqual([
                dict(title=u'repository',
                     uniqueId='http://xml.zeit.de/',
                     url='http://127.0.0.1/repository',
                    ),
                dict(title=u'2006',
                     uniqueId='http://xml.zeit.de/2006',
                     url='http://127.0.0.1/repository/2006',
                    ),
                dict(title=u'DSC00109_2.JPG',
                     uniqueId=u'http://xml.zeit.de/2006/DSC00109_2.JPG',
                     url='http://127.0.0.1/repository/2006/DSC00109_2.JPG',
                    ),
                ], BreadcrumbsView(co).get_breadcrumbs)

    def test_breadcrumbs_work_for_non_content_object(self):
        obj = zeit.cms.workingcopy.interfaces.IWorkingcopy(None)
        self.assertEqual([
                dict(title=u'workingcopy',
                     uniqueId=None,
                     url='http://127.0.0.1/workingcopy',
                    ),
                dict(title=u'zope.user',
                     uniqueId=None,
                     url='http://127.0.0.1/workingcopy/zope.user',
                    ),
                ], BreadcrumbsView(obj).get_breadcrumbs)

    def test_local_content_without_corr_repo_content_lists_name(self):
        content = self.repository['2006']['DSC00109_2.JPG']
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(content)
        co = manager.checkout()
        del self.repository['2006']['DSC00109_2.JPG']
        self.assertEqual([
                dict(title=u'DSC00109_2.JPG',
                     uniqueId=u'http://xml.zeit.de/2006/DSC00109_2.JPG',
                     url='http://127.0.0.1/workingcopy/zope.user/DSC00109_2.JPG',
                    ),
                ], BreadcrumbsView(co).get_breadcrumbs)

    def test_deconfigured_should_use_from_path_only(self):
        import zope.app.appsetup.product
        zope.app.appsetup.product._configs['zeit.cms'][
            'breadcrumbs-use-common-metadata'] = 'false'
        content = zeit.cms.testcontenttype.testcontenttype.TestContentType()
        self.repository['foo'] = content
        view = BreadcrumbsView(content)
        view.get_breadcrumbs_from_path = mock.Mock()
        view.get_breadcrumbs
        self.assertTrue(view.get_breadcrumbs_from_path.called)

    def test_missing_option_should_use_from_path_only(self):
        import zope.app.appsetup.product
        del zope.app.appsetup.product._configs['zeit.cms'][
            'breadcrumbs-use-common-metadata']
        content = zeit.cms.testcontenttype.testcontenttype.TestContentType()
        self.repository['foo'] = content
        view = BreadcrumbsView(content)
        view.get_breadcrumbs_from_path = mock.Mock()
        view.get_breadcrumbs
        self.assertTrue(view.get_breadcrumbs_from_path.called)
