# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.newsletter.newsletter import Newsletter
import gocept.selenium.ztk
import transaction
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zope.component


ZCMLLayer = zeit.cms.testing.ZCMLLayer('ftesting.zcml', product_config=True)


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

    def setUp(self):
        super(SeleniumTestCase, self).setUp()
        with zeit.cms.testing.site(self.getRootFolder()):
            self.repository['newsletter'] = Newsletter()
        transaction.commit()

    def create_content_and_fill_clipboard(self):
        # XXX copy&paste from zeit.content.cp.testing
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction() as principal:
                repository = zope.component.getUtility(
                    zeit.cms.repository.interfaces.IRepository)
                clipboard = zeit.cms.clipboard.interfaces.IClipboard(principal)
                clipboard.addClip('Clip')
                clip = clipboard['Clip']
                for i in range(1, 4):
                    content = (zeit.cms.testcontenttype.testcontenttype.
                               TestContentType())
                    content.teaserTitle = content.shortTeaserTitle = (
                        u'c%s teaser' % i)
                    name = 'c%s' % i
                    repository[name] = content
                    clipboard.addContent(
                        clip, repository[name], name, insert=True)
        transaction.commit()

        s = self.selenium
        s.refresh()
        s.click('//li[@uniqueid="Clip"]')
        s.waitForElementPresent('//li[@uniqueid="Clip"][@action="collapse"]')
