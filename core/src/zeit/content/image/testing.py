import importlib.resources
import os.path

import gocept.httpserverlayer.static
import gocept.selenium
import webtest.forms
import zope.component
import zope.event
import zope.lifecycleevent

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
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(CONFIG_LAYER, features=['zeit.connector.sql.zope'])
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER)


def fixture_bytes(filename, package=None, folder=None):
    if not package:
        package = 'zeit.content.image.browser'
    if not folder:
        folder = 'testdata'
    f = importlib.resources.files(package) / folder / filename
    return f.read_bytes()


def create_image(filename='opernball.jpg', package=None, folder=None):
    image = zeit.content.image.image.LocalImage()
    with image.open('w') as out:
        out.write(fixture_bytes(filename, package, folder))
    image.__name__ = filename
    zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(image))
    return image


def create_image_group(
    filename='DSC00109_2.JPG',
    groupname='group',
    package='zeit.connector',
    folder='testcontent/2006',
):
    repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
    group = zeit.content.image.imagegroup.ImageGroup()
    extension = os.path.splitext(filename)[-1].lower()
    group.master_images = (('desktop', 'master-image' + extension),)
    repository[groupname] = group

    image = create_image(filename, package, folder)
    repository[groupname][group.master_image] = image
    return repository[groupname]


# zope.testbrowser.browser.Control.add_file cannot yet handle multiple file inputs as implemented by
# https://github.com/Pylons/webtest/commit/d1dbc25f53a031d03112cb1e44f4a060cf3665cd
def add_file_multi(control, files):
    control._form[control.name] = [
        webtest.forms.Upload(filename, file, content_type)
        for (file, filename, content_type) in files
    ]


class FixtureLayer(zeit.cms.testing.Layer):
    def setUp(self):
        self['gcs_storage'].stack_push()
        with self['rootFolder'](self['zodbDB-layer']) as root:
            with zeit.cms.testing.site(root):
                repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
                repository['image'] = create_image(
                    'DSC00109_2.JPG', package='zeit.connector', folder='testcontent/2006'
                )
                create_image_group()

    def tearDown(self):
        self['gcs_storage'].stack_pop()


LAYER = FixtureLayer(ZOPE_LAYER)
WSGI_LAYER = zeit.cms.testing.WSGILayer(LAYER)
HTTP_LAYER = zeit.cms.testing.WSGIServerLayer(WSGI_LAYER)
HTTP_STATIC_LAYER = gocept.httpserverlayer.static.Layer(name='HTTPStaticLayer', bases=(HTTP_LAYER,))
WEBDRIVER_LAYER = zeit.cms.testing.WebdriverLayer(HTTP_LAYER)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER


class StaticBrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = HTTP_STATIC_LAYER


class SeleniumTestCase(zeit.cms.testing.SeleniumTestCase):
    layer = WEBDRIVER_LAYER
