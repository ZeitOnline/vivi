# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import pkg_resources
import zeit.cms.repository.interfaces
import zeit.content.image.image
import zeit.content.image.interfaces
import zeit.imp.tests
import zeit.workflow.tests
import zope.app.testing.functional
import zope.component


GalleryLayer = zope.app.testing.functional.ZCMLLayer(
    pkg_resources.resource_filename(__name__, 'ftesting.zcml'),
    __name__, 'GalleryLayer', allow_teardown=True)

GalleryWorkflowLayer = zeit.workflow.tests.WorkflowLayerFactory(
    pkg_resources.resource_filename(__name__, 'ftesting-workflow.zcml'),
    __name__, 'GalleryWorkflowLayer', allow_teardown=True)


product_config = {
    'zeit.content.gallery': {
        'scale-source': 'file://' + pkg_resources.resource_filename(
            __name__, 'scales.xml'),
        'ticket-secret': 'All work and no play makes jack a dull boy.',
}}
product_config.update(zeit.imp.tests.product_config)


def add_image(folder, filename, name=None):
    if name is None:
        name = filename

    filename = pkg_resources(__name__, 'browser/testdata/' + filename)
    test_data = open(filename, 'rb').read()

    image = zeit.content.image.image.LocalImage()
    image.__name__ = name
    image.contentType = 'image/jpeg'
    image.open('w').write(test_data)

    metadata = zeit.content.image.interfaces.IImageMetadata(image)
    metadata.copyrights = ((u'ZEIT online', u'http://www.zeit.de'), )
    metadata.caption = u'Nice <em>01</em> image'

    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    repository[folder][name] = image
