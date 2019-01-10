import gocept.selenium
import logging
import pkg_resources
import plone.testing
import urlparse
import zeit.cms.testing
import zeit.content.text.jinja
import zeit.push.interfaces
import zeit.workflow.testing
import zope.interface


log = logging.getLogger(__name__)


class PushNotifier(object):

    zope.interface.implements(zeit.push.interfaces.IPushNotifier)

    def __init__(self):
        self.reset()

    def reset(self):
        self.calls = []

    def send(self, text, link, **kw):
        self.calls.append((text, link, kw))
        log.info('PushNotifier.send(%s)', dict(
            text=text, link=link, kw=kw))

product_config = """\
<product-config zeit.push>
  twitter-accounts file://{fixtures}/twitter-accounts.xml
  twitter-main-account twitter-test
  twitter-print-account twitter-print
  facebook-accounts file://{fixtures}/facebook-accounts.xml
  facebook-main-account fb-test
  facebook-magazin-account fb-magazin
  facebook-campus-account fb-campus
  push-target-url http://www.zeit.de/
  mobile-image-url http://img.zeit.de/
  urbanairship-audience-group subscriptions
  urbanairship-author-push-template-name authors.json
  mobile-buttons file://{fixtures}/mobile-buttons.xml
  push-payload-templates http://xml.zeit.de/data/urbanairship-templates/
  homepage-banner-uniqueid http://xml.zeit.de/banner
</product-config>
""".format(fixtures=pkg_resources.resource_filename(
    __name__, 'tests/fixtures'))


class ZCMLLayer(zeit.cms.testing.ZCMLLayer):

    def setUp(self):
        # Break circular dependency
        import zeit.content.article.testing
        self.product_config = (
            product_config +
            zeit.cms.testing.cms_product_config +
            zeit.workflow.testing.product_config +
            zeit.content.article.testing.product_config)
        super(ZCMLLayer, self).setUp()


ZCML_LAYER = ZCMLLayer('testing.zcml')


class PushMockLayer(plone.testing.Layer):
    """Helper layer to reset mock notifiers."""

    def testSetUp(self):
        for service in ['urbanairship', 'twitter', 'facebook', 'homepage']:
            notifier = zope.component.getUtility(
                zeit.push.interfaces.IPushNotifier, name=service)
            notifier.reset()

PUSH_MOCK_LAYER = PushMockLayer()


class UrbanairshipTemplateLayer(plone.testing.Layer):

    defaultBases = (ZCML_LAYER,)

    def create_template(self, text=None, name='template.json'):
        if not text:
            text = pkg_resources.resource_string(
                __name__, 'tests/fixtures/payloadtemplate.json')
        with zeit.cms.testing.site(self['functional_setup'].getRootFolder()):
            with zeit.cms.testing.interaction():
                cfg = zope.app.appsetup.product.getProductConfiguration(
                    'zeit.push')
                folder = zeit.cms.content.add.find_or_create_folder(
                    *urlparse.urlparse(
                        cfg['push-payload-templates']).path[1:].split('/'))
                template = zeit.content.text.jinja.JinjaTemplate()
                template.text = text
                template.title = name.split('.')[0].capitalize()
                folder[name] = template

    def setUp(self):
        self['create_template'] = self.create_template

    def testSetUp(self):
        self.create_template('', 'foo.json')
        self.create_template('', 'eilmeldung.json')
        self.create_template(pkg_resources.resource_string(
            __name__, 'tests/fixtures/authors.json'),
            'authors.json')


URBANAIRSHIP_TEMPLATE_LAYER = UrbanairshipTemplateLayer()

LAYER = plone.testing.Layer(
    bases=(URBANAIRSHIP_TEMPLATE_LAYER, PUSH_MOCK_LAYER),
    name='ZCMLPushMockLayer',
    module=__name__)


class TestCase(zeit.cms.testing.FunctionalTestCase):

    layer = LAYER

    def create_payload_template(self, text=None, name='template.json'):
        self.layer['create_template'](text, name)


WSGI_LAYER = zeit.cms.testing.WSGILayer(
    name='WSGILayer', bases=(LAYER,))
HTTP_LAYER = gocept.httpserverlayer.wsgi.Layer(
    name='HTTPLayer', bases=(WSGI_LAYER,))
WD_LAYER = gocept.selenium.WebdriverLayer(
    name='WebdriverLayer', bases=(HTTP_LAYER,))
WEBDRIVER_LAYER = gocept.selenium.WebdriverSeleneseLayer(
    name='WebdriverSeleneseLayer', bases=(WD_LAYER,))
