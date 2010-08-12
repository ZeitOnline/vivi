# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import transaction
import unittest
import zeit.brightcove.interfaces
import zeit.brightcove.testing
import zeit.cms.repository.interfaces
import zeit.cms.testcontenttype.testcontenttype
import zeit.cms.testing
import zeit.content.cp.testing
import zeit.solr.testing
import zope.component
import zope.security.management


def create_content(root):
    with zeit.cms.testing.site(root):
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

        for i in range(3):
            name = 'c%s' % (i + 1)
            c = zeit.cms.testcontenttype.testcontenttype.TestContentType()
            c.teaserTitle = c.shortTeaserTitle = u'%s teaser' % name
            repository[name] = c


CPBrightcoveZCMLLLayer = zeit.cms.testing.ZCMLLayer(
    'ftesting-av.zcml',
    product_config=(zeit.cms.testing.cms_product_config +
                    zeit.brightcove.testing.product_config +
                    zeit.content.cp.testing.product_config +
                    zeit.solr.testing.product_config))


class CPBrightcoveLayer(zeit.brightcove.testing.BrightcoveHTTPLayer,
                        CPBrightcoveZCMLLLayer,
                        zeit.solr.testing.SolrMockLayerBase):

    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def testSetUp(cls):
        root = CPBrightcoveZCMLLLayer.setup.getRootFolder()
        with zeit.cms.testing.site(root):
            repository = zope.component.getUtility(
                zeit.brightcove.interfaces.IRepository)
            repository.update_from_brightcove()
        transaction.commit()

    @classmethod
    def testTearDown(cls):
        pass


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.content.cp.testing.FunctionalDocFileSuite(
        'autopilot.txt',
        'cpextra.txt',
        'fullgraphical.txt',
        'quiz.txt',
        'teaser.txt',
        'teaser-countings.txt',
        'teaser-two-column-layout.txt',
        'teaserbar.txt',
        'xml.txt',
        package='zeit.content.cp.browser.blocks',
        ))
    av_test = zeit.content.cp.testing.FunctionalDocFileSuite(
        'av.txt',
        package='zeit.content.cp.browser.blocks',
        layer=CPBrightcoveLayer)
    suite.addTest(av_test)
    rss_test = zeit.content.cp.testing.FunctionalDocFileSuite(
        'rss.txt',
        package='zeit.content.cp.browser.blocks',
        layer=zeit.content.cp.testing.FeedServer)
    suite.addTest(rss_test)
    return suite
