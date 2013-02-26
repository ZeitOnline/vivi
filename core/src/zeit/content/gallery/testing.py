# Copyright (c) 2009-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import pkg_resources
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.content.image.image
import zeit.content.image.interfaces
import zeit.imp.tests
import zeit.workflow.tests
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


GalleryLayer = zeit.cms.testing.ZCMLLayer(
  'ftesting.zcml',
  product_config=(
    zeit.cms.testing.cms_product_config +
    zeit.imp.tests.product_config +
    product_config))


GalleryWorkflowZCMLLayer = zeit.cms.testing.ZCMLLayer(
  'ftesting-workflow.zcml',
  product_config=(
    zeit.cms.testing.cms_product_config +
    zeit.imp.tests.product_config +
    zeit.workflow.tests.product_config +
    product_config))


class GalleryWorkflowLayer(GalleryWorkflowZCMLLayer,
                           zeit.workflow.tests.WorkflowScriptsLayer):

    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def testSetUp(cls):
        pass

    @classmethod
    def testTearDown(cls):
        pass


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
