# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.selenium.ztk
import zeit.cms.repository.interfaces
import zeit.cms.testing


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


selenium_layer = gocept.selenium.ztk.Layer(ZCMLLayer)


class TestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZCMLLayer


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):

    layer = TestBrowserLayer


class SeleniumTestCase(zeit.cms.testing.SeleniumTestCase):

    layer = selenium_layer
    skin = 'vivi'
