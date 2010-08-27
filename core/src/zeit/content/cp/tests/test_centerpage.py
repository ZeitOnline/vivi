# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.checkout.helper import checked_out
import copy
import gocept.cache.method
import lovely.remotetask.interfaces
import pkg_resources
import transaction
import unittest
import zeit.cms.repository.interfaces
import zeit.cms.testcontenttype.testcontenttype
import zeit.cms.workflow.interfaces
import zeit.content.cp.centerpage
import zeit.content.cp.interfaces
import zeit.content.cp.testing
import zope.app.appsetup.product
import zope.component


class TestCenterPageRSSFeed(zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        super(TestCenterPageRSSFeed, self).setUp()
        # clear rules cache so we get the empty ruleset, so we can publish
        # undisturbed
        gocept.cache.method.clear()

        product_config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.content.cp')
        product_config['rules-url'] = 'file://%s' % (
            pkg_resources.resource_filename(
                'zeit.content.cp.tests.fixtures', 'empty_rules.py'))
        product_config['cp-feed-max-items'] = '5'
        self.repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        cp = zeit.content.cp.centerpage.CenterPage()
        t1 = self.create_teaser(cp)
        t2 = self.create_teaser(cp)

        self.repository['test2'] = (
            zeit.cms.testcontenttype.testcontenttype.TestContentType())
        t1.insert(0, self.repository['testcontent'])
        t2.insert(0, self.repository['test2'])
        self.repository['cp'] = cp

    def create_teaser(self, cp):
        factory = zope.component.getAdapter(
            cp['lead'], zeit.content.cp.interfaces.IElementFactory,
            name='teaser')
        return factory()

    def publish(self, content):
        # for debugging errors during publishing
        # import logging, sys
        # logging.root.handlers = []
        # logging.root.addHandler(logging.StreamHandler(sys.stderr))
        # logging.root.setLevel(logging.DEBUG)

        zeit.cms.workflow.interfaces.IPublish(content).publish()
        tasks = zope.component.getUtility(
            lovely.remotetask.interfaces.ITaskService, 'general')
        tasks.process()
        self.assert_(zeit.cms.workflow.interfaces.IPublishInfo(
            content).published)
        return self.repository.getContent(content.uniqueId)

    def test_teasers_are_added_to_rss_before_publishing(self):
        cp = self.repository['cp']
        self.publish(cp)
        cp = self.repository['cp']
        items = cp.xml.feed.getchildren()
        self.assertEqual(2, len(items))
        self.assertEqual('reference', items[0].tag)
        self.assertEqual('http://xml.zeit.de/test2', items[0].get('href'))
        self.assertEqual('http://xml.zeit.de/testcontent', items[1].get('href'))

    def test_teasers_are_added_only_once(self):
        cp = self.repository['cp']
        self.publish(cp)
        cp = self.repository['cp']

        with checked_out(cp) as working:
            t3 = self.create_teaser(working)
            t3.insert(0, self.repository['testcontent'])
        cp = self.repository['cp']

        self.publish(cp)
        cp = self.repository['cp']
        items = cp.xml.feed.getchildren()
        self.assertEqual(2, len(items))

    def test_number_of_feed_items_is_limited(self):
        cp = self.repository['cp']
        self.publish(cp)
        cp = self.repository['cp']

        def insert_teaser(working, i):
            teaser = self.create_teaser(working)
            name = 'test%s' % i
            self.repository[name] = (
                zeit.cms.testcontenttype.testcontenttype.TestContentType())
            content = self.repository[name]
            teaser.insert(0, content)

        with checked_out(cp) as working:
            for i in range(3, 6):
                insert_teaser(working, i)
        cp = self.repository['cp']

        self.publish(cp)
        cp = self.repository['cp']
        items = cp.xml.feed.getchildren()
        self.assertEqual(5, len(items))
        # the oldest item ('testcontent') has been purged from the list
        expected = ['http://xml.zeit.de/test%s' % i for i in [5, 4, 3, 2]] + [
            'http://xml.zeit.de/testcontent']
        self.assertEqual(expected, [x.get('href') for x in items])
        # The maximum of 5 is extended when there are more than 5 items in the
        # lead:
        with checked_out(cp) as working:
            for i in range(6, 16):
                insert_teaser(working, i)
        cp = self.repository['cp']
        self.publish(cp)
        cp = self.repository['cp']
        items = cp.xml.feed.getchildren()
        self.assertEquals(15, len(items))

        # When the lead shinks, the feed shinks as well
        with checked_out(cp) as working:
            keys = working['lead'].keys()
            for key in keys:
                del working['lead'][key]
        transaction.commit()
        cp = self.repository['cp']
        self.publish(cp)
        cp = self.repository['cp']
        items = cp.xml.feed.getchildren()
        self.assertEquals(5, len(items))

    def test_teasers_are_not_added_to_feed_when_article_was_added(self):
        cp = self.repository['cp']
        cp = self.publish(cp)
        self.assertEqual(
            ['http://xml.zeit.de/test2', 'http://xml.zeit.de/testcontent'],
            [x.get('href') for x in cp.xml.feed.getchildren()])
        # Create a teaser and insert it.
        with checked_out(cp) as working:
            teaser = self.create_teaser(working)
            teaser.insert(0, self.repository['test2'])
            xml_teaser = zope.component.getMultiAdapter(
                (teaser, 0), zeit.content.cp.interfaces.IXMLTeaser)
            xml_teaser.free_teaser = True
        cp = self.repository['cp']
        cp = self.publish(cp)
        # The teaser was not added to the feed because the object it references
        # is already in the feed
        #self.assertEquals(2, len(cp.xml.feed.getchildren()))
        self.assertEqual(
            ['http://xml.zeit.de/test2', 'http://xml.zeit.de/testcontent'],
            [x.get('href') for x in cp.xml.feed.getchildren()])

    def test_articles_are_not_added_to_feed_when_teaser_was_added(self):
        cp = self.repository['cp']
        cp = self.publish(cp)
        self.assertEqual(
            ['http://xml.zeit.de/test2', 'http://xml.zeit.de/testcontent'],
            [x.get('href') for x in cp.xml.feed.getchildren()])
        # Create a teaser and insert it.
        self.repository['content'] = (
            zeit.cms.testcontenttype.testcontenttype.TestContentType())
        with checked_out(cp) as working:
            teaser = self.create_teaser(working)
            teaser.insert(0, self.repository['content'])
            xml_teaser = zope.component.getMultiAdapter(
                (teaser, 0), zeit.content.cp.interfaces.IXMLTeaser)
            xml_teaser.free_teaser = True
        cp = self.publish(cp)
        self.assertEqual(
            [xml_teaser.uniqueId,
             'http://xml.zeit.de/test2',
             'http://xml.zeit.de/testcontent'],
            [x.get('href') for x in cp.xml.feed.getchildren()])
        # When the article is added to the CP the article will not be added to
        # the RSS feed because a teaser referencing the article is already in
        # the feed
        with checked_out(cp) as working:
            teaser = self.create_teaser(working)
            teaser.insert(0, self.repository['content'])
        cp = self.repository['cp']
        cp = self.publish(cp)
        self.assertEqual(
            [xml_teaser.uniqueId,
             'http://xml.zeit.de/test2',
             'http://xml.zeit.de/testcontent'],
            [x.get('href') for x in cp.xml.feed.getchildren()])
