# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.cms.testing
import zeit.wysiwyg.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'filebrowser.txt',
        'image.txt',
        layer=zeit.wysiwyg.testing.WYSIWYGLayer))
    return suite
