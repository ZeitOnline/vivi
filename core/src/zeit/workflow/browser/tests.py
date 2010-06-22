# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import os
import unittest
import zeit.cms.testing
import zeit.workflow.tests
import zope.app.testing.functional


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'indicator.txt',
        'nagios.txt',
        product_config={'zeit.workflow': zeit.workflow.tests.product_config},
        layer=zeit.workflow.tests.WorkflowLayer))
    return suite
