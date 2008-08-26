# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import os
import unittest

import zope.app.testing.functional

import zeit.cms.testing

import zeit.workflow.test


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'indicator.txt',
        product_config={'zeit.workflow': zeit.workflow.test.product_config},
        layer=zeit.workflow.test.WorkflowLayer))
    return suite
