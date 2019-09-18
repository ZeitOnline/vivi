from urlparse import urlparse
import pkg_resources
import plone.testing
import zeit.cmp.testing
import zeit.cms.content.add
import zeit.cms.testing
import zeit.content.text.text
import zope.app.appsetup.product


product_config = """\
<product-config zeit.content.modules>
  jobticker-source file://{base}/tests/fixtures/jobticker.xml
  subject-source file://{base}/tests/fixtures/mail-subjects.xml
  embed-templates http://xml.zeit.de/templates/
</product-config>
""".format(base=pkg_resources.resource_filename(__name__, '.'))


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    product_config, bases=(zeit.cmp.testing.CONFIG_LAYER,))
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))


class EmbedTemplateLayer(plone.testing.Layer):

    defaultBases = (ZOPE_LAYER,)

    def setUp(self):
        with self.__bases__[0].rootFolder(self['zodbDB-layer']) as root:
            with zeit.cms.testing.site(root):
                with zeit.cms.testing.interaction():
                    cfg = zope.app.appsetup.product.getProductConfiguration(
                        'zeit.content.modules')
                    folder = zeit.cms.content.add.find_or_create_folder(
                        *urlparse(cfg['embed-templates']).path[1:].split('/'))
                    template = zeit.content.text.text.Text()
                    template.text = ''
                    folder['twitter.com'] = template


LAYER = EmbedTemplateLayer()


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = LAYER
