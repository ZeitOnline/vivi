# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.content.cp
import zeit.content.cp.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.content.cp.testing.FunctionalDocFileSuite(
        'README.txt',
        'cmscontentiterable.txt',
        'rule.txt',
        'teaser.txt',
        package=zeit.content.cp))
    suite.addTest(zeit.content.cp.testing.FunctionalDocFileSuite(
        'feed.txt',
        layer=zeit.content.cp.testing.FeedServer,
        globs=dict(port=zeit.content.cp.testing.httpd_port),
        package=zeit.content.cp))
    return suite
