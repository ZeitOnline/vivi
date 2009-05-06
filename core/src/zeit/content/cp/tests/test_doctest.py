# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.cms.testing
import zeit.content.cp
import zeit.content.cp.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'cmscontentiterable.txt',
        'rule.txt',
        'teaser.txt',
        'teaserblock.txt',
        package=zeit.content.cp,
        checker=zeit.content.cp.testing.checker,
        product_config=zeit.content.cp.testing.product_config,
        layer=zeit.content.cp.testing.layer))
    return suite
