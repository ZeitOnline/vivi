import importlib.resources

import plone.testing
import zope.component

import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.content.image.image
import zeit.content.image.interfaces
import zeit.crop.testing
import zeit.push.testing


HERE = importlib.resources.files(__package__)
CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {
        'scale-source': f'file://{HERE}/scales.xml',
        'ticket-secret': 'All work and no play makes jack a dull boy',
        'gallery-types-url': f'file://{HERE}/gallery-types.xml',
    },
    bases=(zeit.crop.testing.CONFIG_LAYER, zeit.push.testing.CONFIG_LAYER),
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
PUSH_LAYER = zeit.push.testing.UrbanairshipTemplateLayer(
    name='UrbanairshipTemplateLayer', bases=(ZOPE_LAYER,)
)
LAYER = plone.testing.Layer(bases=(PUSH_LAYER,), name='GalleryLayer')
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER


def add_image(folder, filename, name=None):
    if name is None:
        name = filename

    filename = str((importlib.resources.files(__package__) / 'browser/testdata' / filename))

    image = zeit.content.image.image.LocalImage()
    image.__name__ = name
    with image.open('w') as img:
        with open(filename, 'rb') as f:
            img.write(f.read())

    metadata = zeit.content.image.interfaces.IImageMetadata(image)
    metadata.copyright = (('DIE ZEIT', 'http://www.zeit.de'),)
    metadata.caption = 'Nice image'

    repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
    repository[folder][name] = image
