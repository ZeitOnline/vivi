# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.cms.testing
import zeit.imp.tests


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        package='zeit.imp.browser',
        layer=zeit.imp.tests.imp_layer))
    return suite
