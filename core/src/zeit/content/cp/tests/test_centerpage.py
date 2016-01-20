# coding: utf-8
from xml_compare import xml_compare
from zeit.cms.checkout.helper import checked_out
import lovely.remotetask.interfaces
import lxml.etree
import mock
import pkg_resources
import pyramid_dogpile_cache2
import unittest
import zeit.cms.repository.interfaces
import zeit.cms.testcontenttype.testcontenttype
import zeit.cms.workflow.interfaces
import zeit.content.cp.centerpage
import zeit.content.cp.interfaces
import zeit.content.cp.testing
import zope.app.appsetup.product
import zope.component
import zope.copypastemove.interfaces


class TestCenterPageRSSFeed(zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        super(TestCenterPageRSSFeed, self).setUp()
        # clear rules cache so we get the empty ruleset, so we can publish
        # undisturbed
        pyramid_dogpile_cache2.clear()

        zope.app.appsetup.product.getProductConfiguration(
            'zeit.edit')['rules-url'] = 'file://%s' % (
                pkg_resources.resource_filename(
                    'zeit.content.cp.tests.fixtures', 'empty_rules.py'))
        zope.app.appsetup.product.getProductConfiguration(
            'zeit.content.cp')['cp-feed-max-items'] = '5'
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
        import zeit.edit.interfaces
        factory = zope.component.getAdapter(
            cp['lead'], zeit.edit.interfaces.IElementFactory,
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
        self.assertEqual(
            'http://xml.zeit.de/testcontent', items[1].get('href'))

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
        # self.assertEquals(2, len(cp.xml.feed.getchildren()))
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
            [xml_teaser.original_uniqueId,
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
            [xml_teaser.original_uniqueId,
             'http://xml.zeit.de/test2',
             'http://xml.zeit.de/testcontent'],
            [x.get('href') for x in cp.xml.feed.getchildren()])


class RenderedXMLTest(zeit.content.cp.testing.FunctionalTestCase):

    def create_teaser(self, cp):
        import zeit.edit.interfaces
        factory = zope.component.getAdapter(
            cp['lead'], zeit.edit.interfaces.IElementFactory,
            name='teaser')
        return factory()

    def assertXML(self, expected, actual):
        errors = []
        xml_compare(
            expected, actual, reporter=errors.append, strip_whitespaces=True)
        if errors:
            raise AssertionError('\n'.join(errors))

    def test_without_any_auto_blocks_the_rendered_xml_looks_the_same(self):
        cp = zeit.content.cp.centerpage.CenterPage()
        t1 = self.create_teaser(cp)
        self.create_teaser(cp)
        t1.insert(0, self.repository['testcontent'])

        # IRenderedXML will traverse the CenterPage and adapt contained objects
        # to their interface to create the XML. But adapting the objects may
        # add additional XML attributes, thus we have to run it once to create
        # all attributes and another time to create the final XML repr.
        zeit.content.cp.interfaces.IRenderedXML(cp)
        rendered = zeit.content.cp.interfaces.IRenderedXML(cp)
        # Retrieve original XML after additional attributes were written.
        original = cp.xml

        # Since the CP feed is updated during rendering, we don't want to
        # include it in our comparison.
        original.remove(original.feed)
        rendered.remove(rendered.feed)

        self.assertXML(original, rendered)


class MoveReferencesTest(zeit.content.cp.testing.FunctionalTestCase):

    def create_teaser(self, cp):
        import zeit.edit.interfaces
        factory = zope.component.getAdapter(
            cp['lead'], zeit.edit.interfaces.IElementFactory,
            name='teaser')
        return factory()

    def test_moving_referenced_article_updates_uniqueId_on_cp_checkin(self):
        cp = zeit.content.cp.centerpage.CenterPage()
        t1 = self.create_teaser(cp)
        self.create_teaser(cp)
        t1.insert(0, self.repository['testcontent'])

        zope.copypastemove.interfaces.IObjectMover(
            self.repository['testcontent']).moveTo(
            self.repository, 'changed')
        self.repository['cp'] = cp
        with checked_out(cp):
            pass
        cp = self.repository['cp']
        self.assertIn(
            'http://xml.zeit.de/changed',
            lxml.etree.tostring(cp.xml, pretty_print=True))


class TestContentIter(unittest.TestCase):

    def test_unresolveable_blocks_should_not_be_adapted(self):
        from zeit.content.cp.centerpage import cms_content_iter
        centerpage = mock.Mock()
        centerpage.values = mock.Mock(
            return_value=[mock.sentinel.block1,
                          None,
                          mock.sentinel.block2])
        with mock.patch('zeit.content.cp.interfaces.ICMSContentIterable') as \
                ci:
            cms_content_iter(centerpage)
            self.assertEqual(2, ci.call_count)
            self.assertEqual(
                [((mock.sentinel.block1, ), {}),
                 ((mock.sentinel.block2, ), {})],
                ci.call_args_list)


class CenterpageTest(zeit.content.cp.testing.FunctionalTestCase):

    def test_regression_bug_217_copying_actually_copies(self):
        self.repository['cp'] = zeit.content.cp.centerpage.CenterPage()
        copier = zope.copypastemove.interfaces.IObjectCopier(
            self.repository['cp'])
        copier.copyTo(self.repository['online'])
        with self.assertNothingRaised():
            self.repository['cp']

    def test_handles_unicode_uniqueIds(self):
        content = self.repository[u'ümläut'] = (
            zeit.cms.testcontenttype.testcontenttype.TestContentType())
        cp = zeit.content.cp.centerpage.CenterPage()
        cp['lead'].create_item('teaser').append(content)
        with self.assertNothingRaised():
            cp.updateMetadata(content)
