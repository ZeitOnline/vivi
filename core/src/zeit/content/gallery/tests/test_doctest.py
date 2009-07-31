# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.cms.testing
import zeit.content.gallery.testing
import zeit.workflow.tests


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'reference.txt',
        layer=zeit.content.gallery.testing.GalleryLayer))
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'workflow.txt',
        product_config={'zeit.workflow': zeit.workflow.tests.product_config},
        layer=zeit.content.gallery.testing. GalleryWorkflowLayer))
    return suite
