# Copyright (c) 2007-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.selenium.ztk
import pkg_resources
import re
import shutil
import tempfile
import transaction
import zeit.cms.interfaces
import zeit.cms.tagging.interfaces
import zeit.cms.testing
import zeit.content.author.testing
import zeit.content.cp.testing
import zeit.content.gallery.testing
import zeit.solr.testing
import zeit.workflow.testing
import zope.component
import zope.testing.renormalizing


product_config = """
<product-config zeit.content.article>
    cds-import-valid-path $$ressort/$$year/$$volume
    cds-import-invalid-path cds/invalid/$$year/$$volume
    book-recension-categories file://%s
    genre-url file://%s
    image-layout-source file://%s
    video-layout-source file://%s
</product-config>
""" % (
    pkg_resources.resource_filename(
        __name__, '/tests/recension_categories.xml'),
    pkg_resources.resource_filename(
    __name__, '/tests/article-genres.xml'),
    pkg_resources.resource_filename(
    __name__, '/edit/tests/image-layouts.xml'),
    pkg_resources.resource_filename(
    __name__, '/edit/tests/video-layouts.xml'),
)


checker = zope.testing.renormalizing.RENormalizing([
    (re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'),
     "<GUID>"),])
checker.transformers[0:0] = zeit.cms.testing.checker.transformers


ArticleZCMLLayer = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=(
        product_config +
        zeit.workflow.testing.product_config +
        zeit.content.cp.testing.product_config +
        zeit.content.gallery.testing.product_config +
        zeit.solr.testing.product_config +
        zeit.content.author.testing.product_config +
        zeit.cms.testing.cms_product_config))


class ArticleLayer(ArticleZCMLLayer):

    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def testSetUp(cls):
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        prop = connector._get_properties(
            'http://xml.zeit.de/online/2007/01/Somalia')
        prop[zeit.cms.tagging.testing.KEYWORD_PROPERTY] = (
            'testtag|testtag2|testtag3')

    @classmethod
    def testTearDown(cls):
        pass


class TestBrowserLayer(ArticleLayer):

    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def testSetUp(cls):
        ArticleLayer.setup.setUp()

    @classmethod
    def testTearDown(cls):
        ArticleLayer.setup.tearDown()


CDSZCMLLayer = zeit.cms.testing.ZCMLLayer(
    'cds_ftesting.zcml',
    product_config=(
        product_config +
        zeit.workflow.testing.product_config +
        zeit.content.cp.testing.product_config +
        zeit.cms.testing.cms_product_config))


class CDSLayer(CDSZCMLLayer):

    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def testSetUp(cls):
        product_config = zope.app.appsetup.product._configs[
            'zeit.content.article']
        product_config['cds-export'] = tempfile.mkdtemp()
        product_config['cds-import'] = tempfile.mkdtemp()

    @classmethod
    def testTearDown(cls):
        product_config = zope.app.appsetup.product._configs[
            'zeit.content.article']
        # I don't know why, but those directories get removed automatically
        # somehow.
        try:
            shutil.rmtree(product_config['cds-export'])
        except OSError:
            pass
        try:
            shutil.rmtree(product_config['cds-import'])
        except OSError:
            pass
        del product_config['cds-export']
        del product_config['cds-import']


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ArticleLayer

    def get_article(self):
        from zeit.content.article.article import Article
        from zeit.content.article.interfaces import IArticle
        import zeit.cms.browser.form
        article = Article()
        zeit.cms.browser.form.apply_default_values(article, IArticle)
        article.year = 2011
        article.title = u'title'
        article.ressort = u'Deutschland'
        wl = zope.component.getUtility(
            zeit.cms.tagging.interfaces.IWhitelist)
        article.keywords = (wl['testtag'], wl['testtag2'], wl['testtag3'],)
        return article

    def get_factory(self, article, factory_name):
        import zeit.content.article.edit.body
        import zeit.edit.interfaces
        import zope.component
        body = zeit.content.article.edit.body.EditableBody(
            article, article.xml.body)
        return zope.component.getAdapter(
            body, zeit.edit.interfaces.IElementFactory, factory_name)


selenium_layer = gocept.selenium.ztk.Layer(ArticleLayer)
selenium_workflow_layer = gocept.selenium.ztk.Layer(CDSLayer)

HTTP_LAYER = gocept.httpserverlayer.zopeapptesting.Layer(
    name='HTTPLayer', bases=(ArticleLayer,))
WD_LAYER = gocept.selenium.WebdriverLayer(
    name='WebdriverLayer', bases=(HTTP_LAYER,))
WEBDRIVER_LAYER = gocept.selenium.WebdriverSeleneseLayer(
    name='WebdriverSeleneseLayer', bases=(WD_LAYER,))


class SeleniumTestCase(zeit.cms.testing.SeleniumTestCase):

    layer = selenium_layer

    WIDGET_SELECTOR = 'xpath=//label[@for="%s"]/../../*[@class="widget"]'

    def assert_widget_text(self, widget_id, text):
        path = self.WIDGET_SELECTOR % widget_id
        self.selenium.waitForElementPresent(path)
        self.selenium.assertText(path, text)

    def wait_for_widget_text(self, widget_id, text):
        path = self.WIDGET_SELECTOR % widget_id
        self.selenium.waitForElementPresent(path)
        self.selenium.waitForText(path, text)
