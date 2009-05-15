# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import os
import unittest
import zeit.cms.testing
import zope.app.testing.functional

SearchLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'SearchLayer', allow_teardown=True)

def test_suite():
    suite = unittest.TestSuite()
    return suite
