# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.content.cp
import zeit.content.cp.testing


def test_suite():
    return zeit.content.cp.testing.FunctionalDocFileSuite(
        'README.txt',
        'cmscontentiterable.txt',
        'rule.txt',
        'teaser.txt',
        'teaserblock.txt')
