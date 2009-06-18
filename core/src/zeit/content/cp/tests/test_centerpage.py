# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import copy
import gocept.cache.method
import lovely.remotetask.interfaces
import pkg_resources
import unittest
import zeit.cms.repository.interfaces
import zeit.cms.testcontenttype.testcontenttype
import zeit.cms.workflow.interfaces
import zeit.content.cp.centerpage
import zeit.content.cp.interfaces
import zeit.content.cp.testing
import zope.component


class CenterPageTest(zeit.content.cp.testing.FunctionalTestCase):

    def __init__(self, *args, **kw):
        self.product_config = copy.deepcopy(self.product_config)
        self.product_config['zeit.content.cp']['rules-url'] = 'file://%s' % (
            pkg_resources.resource_filename(
            'zeit.content.cp.tests.fixtures', 'empty_rules.py'))
        super(CenterPageTest, self).__init__(*args, **kw)

    def setUp(self):
        super(CenterPageTest, self).setUp()
        # clear rules cache so we get the empty ruleset, so we can publish
        # undisturbed
        gocept.cache.method.clear()

        self.repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        self.cp = zeit.content.cp.centerpage.CenterPage()
        factory = zope.component.getAdapter(
            self.cp['lead'], zeit.content.cp.interfaces.IElementFactory,
            name='teaser')
        self.t1 = factory()
        self.t2 = factory()

        self.repository['t2'] = (
            zeit.cms.testcontenttype.testcontenttype.TestContentType())
        self.t1.insert(0, self.repository['testcontent'])
        self.t2.insert(0, self.repository['t2'])
        self.repository['2007']['cp'] = self.cp
        self.cp = self.repository['2007']['cp']

    def _publish(self):
        # for debugging errors during publishing
#         import logging, sys
#         logging.root.handlers = []
#         logging.root.addHandler(logging.StreamHandler(sys.stderr))
#         logging.root.setLevel(logging.DEBUG)

        zeit.cms.workflow.interfaces.IPublish(self.cp).publish()
        tasks = zope.component.getUtility(
            lovely.remotetask.interfaces.ITaskService, 'general')
        tasks.process()
        self.assert_(zeit.cms.workflow.interfaces.IPublishInfo(
            self.cp).published)

    def test_teasers_are_added_to_rss_before_publishing(self):
        self._publish()
        items = self.cp.xml.feed.getchildren()
        self.assertEqual(2, len(items))
        self.assertEqual('reference', items[0].tag)
        self.assertEqual('http://xml.zeit.de/testcontent', items[0].get('href'))


def test_suite():
    return unittest.makeSuite(CenterPageTest)
