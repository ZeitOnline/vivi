import gocept.httpserverlayer.wsgi
import gocept.selenium
import pkg_resources
import plone.testing
import re
import shutil
import tempfile
import zeit.cms.tagging.interfaces
import zeit.cms.tagging.testing
import zeit.cms.testing
import zeit.content.author.testing
import zeit.content.cp.testing
import zeit.content.gallery.testing
import zeit.content.image.testing
import zeit.content.volume.testing
import zeit.push
import zeit.workflow.testing
import zope.component
import zope.testing.renormalizing


product_config = """
<product-config zeit.content.article>
  cds-import-valid-path $$ressort/$$year/$$volume
  cds-import-invalid-path cds/invalid/$$year/$$volume
  book-recension-categories file://{base}/tests/recension_categories.xml
  genre-url file://{base}/tests/article-genres.xml
  image-display-mode-source file://{base}/edit/tests/image-display-modes.xml
  legacy-display-mode-source file://{base}/edit/tests/legacy-display-modes.xml
  image-variant-name-source file://{base}/edit/tests/image-variant-names.xml
  legacy-variant-name-source file://{base}/edit/tests/legacy-variant-names.xml
  video-layout-source file://{base}/edit/tests/video-layouts.xml
  htmlblock-layout-source file://{base}/edit/tests/htmlblock-layouts.xml
  infobox-layout-source file://{base}/edit/tests/infobox-layouts.xml
  template-source file://{base}/edit/tests/templates.xml
  header-module-source file://{base}/edit/tests/header-modules.xml
</product-config>
""".format(base=pkg_resources.resource_filename(__name__, ''))


checker = zope.testing.renormalizing.RENormalizing([
    (re.compile(
        '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'),
     "<GUID>")])
checker.transformers[0:0] = zeit.cms.testing.checker.transformers


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=(
        product_config +
        zeit.workflow.testing.product_config +
        zeit.content.cp.testing.product_config +
        zeit.content.image.testing.product_config +
        zeit.content.gallery.testing.product_config +
        zeit.content.author.testing.product_config +
        zeit.content.volume.testing.product_config +
        zeit.push.product_config +
        zeit.cms.testing.cms_product_config))


class ArticleLayer(plone.testing.Layer):

    defaultBases = (ZCML_LAYER,)

    def testSetUp(self):
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        prop = connector._get_properties(
            'http://xml.zeit.de/online/2007/01/Somalia')
        prop[zeit.cms.tagging.testing.KEYWORD_PROPERTY] = (
            'testtag|testtag2|testtag3')

LAYER = ArticleLayer()


CDS_ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'cds_ftesting.zcml',
    product_config=(
        product_config +
        zeit.workflow.testing.product_config +
        zeit.content.cp.testing.product_config +
        zeit.cms.testing.cms_product_config))


class CDSLayer(plone.testing.Layer):

    defaultBases = (CDS_ZCML_LAYER,)

    def testSetUp(self):
        product_config = zope.app.appsetup.product._configs[
            'zeit.content.article']
        product_config['cds-export'] = tempfile.mkdtemp()
        product_config['cds-import'] = tempfile.mkdtemp()

    def testTearDown(self):
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

CDS_LAYER = CDSLayer()


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase,
                         zeit.cms.tagging.testing.TaggingHelper):

    layer = LAYER

    def setUp(self):
        super(FunctionalTestCase, self).setUp()
        self.setup_tags('testtag', 'testtag2', 'testtag3')

    def get_article(self):

        wl = zope.component.getUtility(
            zeit.cms.tagging.interfaces.IWhitelist)
        article = create_article()
        article.keywords = [
            wl.get(tag) for tag in ('testtag', 'testtag2', 'testtag3')]
        return article

    def get_factory(self, article, factory_name):
        import zeit.content.article.edit.body
        import zeit.edit.interfaces
        import zope.component
        body = zeit.content.article.edit.body.EditableBody(
            article, article.xml.body)
        return zope.component.getAdapter(
            body, zeit.edit.interfaces.IElementFactory, factory_name)


def create_article():
    from zeit.content.article.article import Article
    from zeit.content.article.interfaces import IArticle
    import zeit.cms.browser.form
    article = Article()
    zeit.cms.browser.form.apply_default_values(article, IArticle)
    article.year = 2011
    article.title = u'title'
    article.ressort = u'Deutschland'
    zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(article))
    return article


WSGI_LAYER = zeit.cms.testing.WSGILayer(
    name='WSGILayer', bases=(LAYER,))
HTTP_LAYER = gocept.httpserverlayer.wsgi.Layer(
    name='HTTPLayer', bases=(WSGI_LAYER,))
WD_LAYER = gocept.selenium.WebdriverLayer(
    name='WebdriverLayer', bases=(HTTP_LAYER,))
WEBDRIVER_LAYER = gocept.selenium.WebdriverSeleneseLayer(
    name='WebdriverSeleneseLayer', bases=(WD_LAYER,))


class SeleniumTestCase(zeit.cms.testing.SeleniumTestCase):

    layer = WEBDRIVER_LAYER

    WIDGET_SELECTOR = 'xpath=//label[@for="%s"]/../../*[@class="widget"]'

    def assert_widget_text(self, widget_id, text):
        path = self.WIDGET_SELECTOR % widget_id
        self.selenium.waitForElementPresent(path)
        self.selenium.assertText(path, text)

    def wait_for_widget_text(self, widget_id, text):
        path = self.WIDGET_SELECTOR % widget_id
        self.selenium.waitForElementPresent(path)
        self.selenium.waitForText(path, text)
