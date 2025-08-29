import importlib.resources
import os.path

import gocept.httpserverlayer.static
import gocept.selenium
import webtest.forms
import zope.component

from zeit.cms.repository.folder import Folder
import zeit.cms.repository.interfaces
import zeit.cms.testcontenttype.testcontenttype
import zeit.cms.testing
import zeit.content.image.image
import zeit.content.image.imagegroup


HERE = importlib.resources.files(__package__)
CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {
        'display-type-source': f'file://{HERE}/tests/fixtures/display-types.xml',
        'variant-source': f'file://{HERE}/tests/fixtures/variants.xml',
        'copyright-company-source': f'file://{HERE}/tests/fixtures/copyright-company.xml',
        'encoder-parameters': f'file://{HERE}/tests/fixtures/encoders.xml',
        'mdb-api-url': 'http://example.invalid',
        'mdb-api-username': 'mdbuser',
        'mdb-api-password': 'mdbpass',
    },
    bases=zeit.cms.testing.CONFIG_LAYER,
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=CONFIG_LAYER, features=['zeit.connector.sql'])
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER)
WSGI_LAYER = zeit.cms.testing.WSGILayer(ZOPE_LAYER)
HTTP_LAYER = zeit.cms.testing.WSGIServerLayer(WSGI_LAYER)
HTTP_STATIC_LAYER = gocept.httpserverlayer.static.Layer(name='HTTPStaticLayer', bases=(HTTP_LAYER,))
WEBDRIVER_LAYER = zeit.cms.testing.WebdriverLayer(HTTP_LAYER)


def fixture_bytes(filename, package=None, folder=None):
    if not package:
        package = 'zeit.content.image.browser'
    if not folder:
        folder = 'testdata'
    f = importlib.resources.files(package) / folder / filename
    return f.read_bytes()


def create_local_image(filename='opernball.jpg', package=None, folder=None):
    image = zeit.content.image.image.LocalImage()
    with image.open('w') as out:
        out.write(fixture_bytes(filename, package, folder))
    image.__name__ = filename
    return image


def create_image_group():
    repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
    repository['image-group'] = zeit.content.image.imagegroup.ImageGroup()
    group = repository['image-group']
    for filename in (
        'new-hampshire-450x200.jpg',
        'new-hampshire-artikel.jpg',
        'obama-clinton-120x120.jpg',
    ):
        group[filename] = create_local_image(filename)
    return group


def create_image_group_with_master_image(filename=None):
    repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
    if filename is None:
        filename = 'DSC00109_2.JPG'
        repository['2006'] = Folder()
        image = create_local_image(filename, 'zeit.connector', 'testcontent/2006')
        repository['2006'][filename] = image
        fh = repository['2006'][filename].open()
    else:
        fh = open(filename, 'rb')
    extension = os.path.splitext(filename)[-1].lower()

    group = zeit.content.image.imagegroup.ImageGroup()
    group.master_images = (('desktop', 'master-image' + extension),)
    repository['group'] = group
    image = zeit.content.image.image.LocalImage()
    with image.open('w') as out:
        out.write(fh.read())
    fh.close()
    repository['group'][group.master_image] = image
    return repository['group']


# zope.testbrowser.browser.Control.add_file cannot yet handle multiple file inputs as implemented by
# https://github.com/Pylons/webtest/commit/d1dbc25f53a031d03112cb1e44f4a060cf3665cd
def add_file_multi(control, files):
    control._form[control.name] = [
        webtest.forms.Upload(filename, file, content_type)
        for (file, filename, content_type) in files
    ]


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER


class StaticBrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = HTTP_STATIC_LAYER


class SeleniumTestCase(zeit.cms.testing.SeleniumTestCase):
    layer = WEBDRIVER_LAYER
