from zeit.content.video.testing import PLAYER_MOCK_LAYER
from zeit.newsletter.newsletter import Newsletter
import gocept.selenium
import plone.testing
import transaction
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.content.image.testing
import zeit.content.video.testing
import zope.app.appsetup.product
import zope.component


product_config = """\
<product-config zeit.newsletter>
    renderer-host file:///dev/null
</product-config>
"""

CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(product_config, bases=(
    zeit.content.image.testing.CONFIG_LAYER,))
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER, PLAYER_MOCK_LAYER))
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(ZOPE_LAYER,))
HTTP_LAYER = zeit.cms.testing.WSGIServerLayer(
    name='HTTPLayer', bases=(WSGI_LAYER,))
WD_LAYER = zeit.cms.testing.WebdriverLayer(
    name='WebdriverLayer', bases=(HTTP_LAYER,))
WEBDRIVER_LAYER = gocept.selenium.WebdriverSeleneseLayer(
    name='WebdriverSeleneseLayer', bases=(WD_LAYER,))


class TestBrowserLayer(plone.testing.Layer):

    defaultBases = (WSGI_LAYER,)

    def setUp(self):
        product_config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        product_config['publish-script'] = 'true'
        product_config['retract-script'] = 'true'


BROWSER_LAYER = TestBrowserLayer()


class TestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZOPE_LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):

    layer = BROWSER_LAYER


class SeleniumTestCase(zeit.cms.testing.SeleniumTestCase):

    layer = WEBDRIVER_LAYER
    skin = 'vivi'

    def setUp(self):
        super().setUp()
        self.repository['newsletter'] = Newsletter()
        transaction.commit()

    def create_content_and_fill_clipboard(self):
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        principal = (zope.security.management.getInteraction()
                     .participations[0].principal)
        clipboard = zeit.cms.clipboard.interfaces.IClipboard(principal)
        clipboard.addClip('Clip')
        clip = clipboard['Clip']
        for i in range(1, 4):
            content = (zeit.cms.testcontenttype.testcontenttype.
                       ExampleContentType())
            content.teaserTitle = content.shortTeaserTitle = (
                'c%s teaser' % i)
            name = 'c%s' % i
            repository[name] = content
            clipboard.addContent(
                clip, repository[name], name, insert=True)
        transaction.commit()

        s = self.selenium
        s.refresh()
        s.waitForElementPresent('//li[@uniqueid="Clip"]')
        s.clickAt('//li[@uniqueid="Clip"]', '10,10')
        s.waitForElementPresent('//li[@uniqueid="Clip"][@action="collapse"]')
