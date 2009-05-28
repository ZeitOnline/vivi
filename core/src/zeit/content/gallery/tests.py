# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import os
import unittest
import zeit.cms.testing
import zeit.workflow.tests
import zope.app.testing.functional


GalleryLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'GalleryLayer', allow_teardown=True)

GalleryWorkflowLayer = zeit.workflow.tests.WorkflowLayerFactory(
    os.path.join(os.path.dirname(__file__), 'ftesting-workflow.zcml'),
    __name__, 'GalleryWorkflowLayer', allow_teardown=True)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'reference.txt',
        layer=GalleryLayer))
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'workflow.txt',
        product_config={'zeit.workflow': zeit.workflow.tests.product_config},
        layer=GalleryWorkflowLayer))
    return suite
