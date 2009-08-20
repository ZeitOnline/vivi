# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.repository.interfaces
import zeit.cms.sitecontrol.tree
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

    def test_toplevel_should_contain_ressorts(self):
        root = self.tree.getTreeData()[0]
        self.assertEqual(u'Start', root['title'])
        deutschland = root['sub_data'][0]
        # this test relies on the testcontent in the mock connector
        # where Deutschland is the only ressort that exists
        self.assertEqual(u'Deutschland', deutschland['title'])

        self.assertEqual(
            'http://127.0.0.1/repository/Deutschland/index/@@checkout',
            deutschland['url'])

    def test_ressort_should_contain_subressorts(self):
        root = self.tree.getTreeData()[0]
        deutschland = root['sub_data'][0]
        self.tree.expandNode(deutschland['uniqueId'])
        root = self.tree.getTreeData()[0]
        deutschland = root['sub_data'][0]
        self.assertEqual(u'Integration', deutschland['sub_data'][0]['title'])
