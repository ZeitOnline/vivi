# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import random
import unittest
import z3c.etestbrowser.testing
import zeit.content.cp.browser.blocks
import zeit.content.cp.browser.tests
import zeit.content.cp.testing
import zope.security.management
import zope.site.hooks


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
        'teaserbar.txt',
        'xml.txt',
        ))
    return suite
