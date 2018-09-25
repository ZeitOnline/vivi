import pkg_resources
import plone.testing
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.content.image.image
import zeit.content.image.interfaces
import zeit.content.image.testing
import zeit.imp.tests
import zeit.push.testing
import zeit.workflow.testing
import zope.component


product_config = """
<product-config zeit.content.gallery>
    scale-source file://%s
    ticket-secret All work and no play makes jack a dull boy
    gallery-types-url file://%s
</product-config>
""" % (
    pkg_resources.resource_filename(__name__, 'scales.xml'),
    pkg_resources.resource_filename(__name__, 'gallery-types.xml'),
)


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=(
        zeit.cms.testing.cms_product_config +
        zeit.content.image.testing.product_config +
        zeit.imp.tests.product_config +
        zeit.push.testing.product_config +
        product_config))

PUSH_LAYER = zeit.push.testing.UrbanairshipTemplateLayer(
    name='UrbanairshipTemplateLayer', bases=(ZCML_LAYER,))

LAYER = plone.testing.Layer(bases=(PUSH_LAYER,), name='GalleryLayer')

WORKFLOW_ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting-workflow.zcml',
    product_config=(
        zeit.cms.testing.cms_product_config +
        zeit.imp.tests.product_config +
        zeit.workflow.testing.product_config +
        zeit.push.testing.product_config +
        product_config))


WORKFLOW_LAYER = plone.testing.Layer(
    name='GalleryWorkflowLayer', module=__name__,
    bases=(WORKFLOW_ZCML_LAYER, zeit.workflow.testing.SCRIPTS_LAYER))


def add_image(folder, filename, name=None):
    if name is None:
        name = filename

    filename = pkg_resources.resource_filename(
        __name__, 'browser/testdata/' + filename)
    test_data = open(filename, 'rb').read()

    image = zeit.content.image.image.LocalImage()
    image.__name__ = name
    image.contentType = 'image/jpeg'
    image.open('w').write(test_data)

    metadata = zeit.content.image.interfaces.IImageMetadata(image)
    metadata.copyrights = ((u'ZEIT online', u'http://www.zeit.de'), )
    metadata.caption = u'Nice image'

    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    repository[folder][name] = image
