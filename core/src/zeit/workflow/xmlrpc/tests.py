# Copyright (c) 2008-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.testing import doctest
import unittest
import zeit.cms.testing
import zeit.workflow.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=zeit.workflow.testing.WorkflowLayer,
        product_config={'zeit.workflow': zeit.workflow.testing.product_config}
    ))
    return suite
