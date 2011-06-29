# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest2 as unittest
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zope.component
import zope.component.hooks
import zope.testbrowser.testing


ZCMLLayer = zeit.cms.testing.ZCMLLayer('ftesting.zcml')


class TestBrowserLayer(ZCMLLayer):

    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def testSetUp(cls):
        ZCMLLayer.setup.setUp()

    @classmethod
    def testTearDown(cls):
        ZCMLLayer.setup.tearDown()


class TestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZCMLLayer


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):

    layer = TestBrowserLayer
