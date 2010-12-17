# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.cms.testing
import zeit.workflow.testing

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'dependency.txt',
        'syndication.txt',
        layer=zeit.workflow.testing.WorkflowLayer,
        package='zeit.workflow'))
    return suite
