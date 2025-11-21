import importlib.resources

import transaction
import zope.component

from zeit.cms.repository.folder import Folder
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.content.image.image
import zeit.content.image.interfaces
import zeit.crop.testing
import zeit.push.testing


def create_fixture(repository):
    repository['folder'] = Folder()
    zeit.content.gallery.testing.add_image('folder', '01.jpg')
    zeit.content.gallery.testing.add_image('folder', '02.jpg')
    zeit.content.gallery.testing.add_image('folder', '03.jpg')
    transaction.commit()
    gallery = zeit.content.gallery.gallery.Gallery()
    gallery.image_folder = repository['folder']
    repository['gallery'] = gallery

    transaction.commit()

    zeit.push.testing.create_fixture(repository)


HERE = importlib.resources.files(__package__)
CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {
        'scale-source': f'file://{HERE}/scales.xml',
        'gallery-types-url': f'file://{HERE}/gallery-types.xml',
    },
    bases=(zeit.crop.testing.CONFIG_LAYER, zeit.push.testing.CONFIG_LAYER),
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(CONFIG_LAYER, features=['zeit.connector.sql.zope'])
_zope_layer = zeit.cms.testing.RawZopeLayer(ZCML_LAYER)


ZOPE_LAYER = zeit.cms.testing.SQLIsolationSavepointLayer(_zope_layer, create_fixture)


WSGI_LAYER = zeit.cms.testing.WSGILayer(ZOPE_LAYER)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER


def add_image(folder, filename, name=None):
    if name is None:
        name = filename

    image = zeit.content.image.testing.create_image(filename, __package__, 'browser/testdata')
    metadata = zeit.content.image.interfaces.IImageMetadata(image)
    metadata.copyright = (('DIE ZEIT', 'http://www.zeit.de'),)
    metadata.caption = 'Nice image'

    repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
    repository[folder][name] = image
    transaction.commit()
