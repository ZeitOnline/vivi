# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import random
import unittest
import z3c.etestbrowser.testing
import zeit.cms.repository.interfaces
import zeit.cms.testcontenttype.testcontenttype
import zeit.content.cp.browser.blocks
import zeit.content.cp.browser.tests
import zeit.content.cp.testing
import zope.component
import zope.security.management
import zope.site.hooks


def create_content(root):
    old_site = zope.site.hooks.getSite()
    zope.site.hooks.setSite(root)
    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)

    for i in range(3):
        name = 'c%s' % (i + 1)
        c = zeit.cms.testcontenttype.testcontenttype.TestContentType()
        c.teaserTitle = c.shortTeaserTitle = u'%s teaser' % name
        repository[name] = c

    zope.site.hooks.setSite(old_site)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.content.cp.testing.FunctionalDocFileSuite(
        'av.txt',
        'autopilot.txt',
        'cpextra.txt',
        'fullgraphical.txt',
        'quiz.txt',
        'rss.txt',
        'teaser.txt',
        'teaser-two-column-layout.txt',
        'teaserbar.txt',
        'xml.txt',
        ))
    return suite
