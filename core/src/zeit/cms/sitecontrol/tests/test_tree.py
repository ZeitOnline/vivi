# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.repository.interfaces
import zeit.cms.sitecontrol.tree
import zeit.cms.testcontenttype.testcontenttype
import zeit.cms.testing
import zope.component
import zope.publisher.browser
import zope.security.testing


class TreeTest(zeit.cms.testing.FunctionalTestCase):

    def setUp(self):
        super(TreeTest, self).setUp()

        principal = zope.security.testing.Principal('zope.user')
        request = zope.publisher.browser.TestRequest()
        request.setPrincipal(principal)

        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        self.tree = zeit.cms.sitecontrol.tree.Tree(repository, request)

        repository['deutschland'] = zeit.cms.repository.folder.Folder()
        repository['deutschland']['index'] = (
            zeit.cms.testcontenttype.testcontenttype.TestContentType())
        repository['deutschland']['integration'] = (
            zeit.cms.repository.folder.Folder())

    def test_toplevel_should_contain_ressorts(self):
        root = self.tree.getTreeData()[0]
        self.assertEqual(u'Homepage', root['title'])
        self.assertEqual(True, root['subfolders'])
        deutschland = root['sub_data'][0]
        self.assertEqual(u'Deutschland', deutschland['title'])
        self.assertEqual(True, deutschland['subfolders'])

        self.assertEqual(
            'http://127.0.0.1/repository/deutschland/index/@@view.html',
            deutschland['url'])

    def test_ressort_should_contain_subressorts(self):
        root = self.tree.getTreeData()[0]
        deutschland = root['sub_data'][0]
        self.tree.expandNode(deutschland['uniqueId'])
        root = self.tree.getTreeData()[0]
        deutschland = root['sub_data'][0]
        integration = deutschland['sub_data'][0]
        self.assertEqual(u'Integration', integration['title'])
        self.assertEqual(False, integration['subfolders'])
        self.assertEqual(
            'http://127.0.0.1/repository/deutschland/integration',
            integration['url'])
