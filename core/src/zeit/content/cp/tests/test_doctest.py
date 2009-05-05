# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import pkg_resources
import re
import unittest
import zeit.cms.testing
import zeit.content.cp
import zeit.content.cp.testing
import zope.app.testing.functional


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'teaser.txt',
        'teaserblock.txt',
        'cmscontentiterable.txt',
        'rule.txt',
        package=zeit.content.cp,
        checker=zeit.content.cp.testing.checker,
        layer=zeit.content.cp.testing.layer))
    return suite
