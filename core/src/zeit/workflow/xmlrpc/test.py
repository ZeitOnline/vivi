# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest

from zope.testing import doctest

import zeit.cms.testing
import zeit.workflow.test


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=zeit.workflow.test.WorkflowLayer,
        product_config={'zeit.workflow': zeit.workflow.test.product_config},
        optionflags=(doctest.INTERPRET_FOOTNOTES|doctest.ELLIPSIS|
                     doctest.REPORT_NDIFF|doctest.NORMALIZE_WHITESPACE)))
    return suite
