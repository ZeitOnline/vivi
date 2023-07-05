import pkg_resources
import plone.testing
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.content.image.image
import zeit.content.image.interfaces
import zeit.imp.tests
import zeit.push.testing
import zeit.workflow.testing
import zope.component


product_config = """
<product-config zeit.content.gallery>
    scale-source file://{base}/scales.xml
    ticket-secret All work and no play makes jack a dull boy
    gallery-types-url file://{base}/gallery-types.xml
</product-config>
""".format(base=pkg_resources.resource_filename(__name__, ''))


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(product_config, bases=(
    zeit.imp.tests.CONFIG_LAYER,
    zeit.push.testing.CONFIG_LAYER))
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
PUSH_LAYER = zeit.push.testing.UrbanairshipTemplateLayer(
    name='UrbanairshipTemplateLayer', bases=(ZOPE_LAYER,))
LAYER = plone.testing.Layer(bases=(PUSH_LAYER,), name='GalleryLayer')
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZOPE_LAYER


def add_image(folder, filename, name=None):
    if name is None:
        name = filename

    filename = pkg_resources.resource_filename(
        __name__, 'browser/testdata/' + filename)

    image = zeit.content.image.image.LocalImage()
    image.__name__ = name
    image.contentType = 'image/jpeg'
    with image.open('w') as img:
        with open(filename, 'rb') as f:
            img.write(f.read())

    metadata = zeit.content.image.interfaces.IImageMetadata(image)
    metadata.copyright = (('ZEIT online', 'http://www.zeit.de'),)
    metadata.caption = 'Nice image'

    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    repository[folder][name] = image
