# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from __future__ import with_statement
from zeit.cms.checkout.helper import checked_out
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
        cp = zeit.content.cp.centerpage.CenterPage()
        self.t1 = self.create_teaser(cp)
        self.t2 = self.create_teaser(cp)

        self.repository['t2'] = (
            zeit.cms.testcontenttype.testcontenttype.TestContentType())
        self.t1.insert(0, self.repository['testcontent'])
        self.t2.insert(0, self.repository['t2'])
        self.repository['cp'] = cp

    def create_teaser(self, cp):
        factory = zope.component.getAdapter(
            cp['lead'], zeit.content.cp.interfaces.IElementFactory,
            name='teaser')
        return factory()

    def publish(self, content):
        # for debugging errors during publishing
#         import logging, sys
#         logging.root.handlers = []
#         logging.root.addHandler(logging.StreamHandler(sys.stderr))
#         logging.root.setLevel(logging.DEBUG)

        zeit.cms.workflow.interfaces.IPublish(content).publish()
        tasks = zope.component.getUtility(
            lovely.remotetask.interfaces.ITaskService, 'general')
        tasks.process()
        self.assert_(zeit.cms.workflow.interfaces.IPublishInfo(
            content).published)

    def test_teasers_are_added_to_rss_before_publishing(self):
        cp = self.repository['cp']
        self.publish(cp)
        items = cp.xml.feed.getchildren()
        self.assertEqual(2, len(items))
        self.assertEqual('reference', items[0].tag)
        self.assertEqual('http://xml.zeit.de/testcontent', items[0].get('href'))
        self.assertEqual('http://xml.zeit.de/t2', items[1].get('href'))

    def test_teasers_are_added_only_once(self):
        cp = self.repository['cp']
        self.publish(cp)

        with checked_out(cp) as working:
            t3 = self.create_teaser(working)
            t3.insert(0, self.repository['testcontent'])
        cp = self.repository['cp']

        self.publish(cp)
        items = cp.xml.feed.getchildren()
        self.assertEqual(2, len(items))
        self.assertEqual('reference', items[0].tag)
        self.assertEqual('http://xml.zeit.de/testcontent', items[0].get('href'))
        self.assertEqual('http://xml.zeit.de/t2', items[1].get('href'))


def test_suite():
    return unittest.makeSuite(CenterPageTest)
