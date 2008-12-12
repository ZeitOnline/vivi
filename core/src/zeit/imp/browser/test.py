# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import os.path
import unittest
import zeit.cms.testing
import zeit.imp.test


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=zeit.imp.test.imp_layer))
    return suite
