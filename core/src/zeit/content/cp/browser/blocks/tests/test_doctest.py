# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import transaction
import unittest
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


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.content.cp.testing.FunctionalDocFileSuite(
        'autopilot.txt',
        'av.txt',
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
    rss_test = zeit.content.cp.testing.FunctionalDocFileSuite(
        'rss.txt',
        package='zeit.content.cp.browser.blocks',
        layer=zeit.content.cp.testing.FeedServer)
    suite.addTest(rss_test)
    return suite
