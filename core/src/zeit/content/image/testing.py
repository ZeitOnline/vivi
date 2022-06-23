import gocept.httpserverlayer.static
import gocept.selenium
import os.path
import pkg_resources
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.content.image.image
import zeit.content.image.imagegroup
import zeit.workflow.testing
import zope.component


product_config = """
<product-config zeit.content.image>
    display-type-source file://{here}/tests/fixtures/display-types.xml
    variant-source file://{here}/tests/fixtures/variants.xml
    copyright-company-source file://{here}/tests/fixtures/copyright-company.xml
    encoder-parameters file://{here}/tests/fixtures/encoders.xml
    mdb-api-url http://example.invalid
    mdb-api-username mdbuser
    mdb-api-password mdbpass
</product-config>
""".format(here=pkg_resources.resource_filename(__name__, '.'))


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(product_config, bases=(
    zeit.workflow.testing.CONFIG_LAYER,))
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(ZOPE_LAYER,))
HTTP_LAYER = zeit.cms.testing.WSGIServerLayer(
    name='HTTPLayer', bases=(WSGI_LAYER,))
HTTP_STATIC_LAYER = gocept.httpserverlayer.static.Layer(
    name='HTTPStaticLayer',
    bases=(HTTP_LAYER,))

WD_LAYER = zeit.cms.testing.WebdriverLayer(
    name='WebdriverLayer', bases=(HTTP_LAYER,))
WEBDRIVER_LAYER = gocept.selenium.WebdriverSeleneseLayer(
    name='WebdriverSeleneseLayer', bases=(WD_LAYER,))


def create_local_image(filename, path='browser/testdata/'):
    image = zeit.content.image.image.LocalImage()
    with image.open('w') as out:
        file_name = pkg_resources.resource_filename(
            __name__, '%s%s' % (path, filename))
        with open(file_name, 'rb') as fh:
            out.write(fh.read())
    image.__name__ = filename
    return image


def create_image_group():
    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    repository['image-group'] = zeit.content.image.imagegroup.ImageGroup()
    group = repository['image-group']
    for filename in ('new-hampshire-450x200.jpg',
                     'new-hampshire-artikel.jpg',
                     'obama-clinton-120x120.jpg'):
        group[filename] = create_local_image(filename)
    return group


def create_image_group_with_master_image(file_name=None):
    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    if file_name is None:
        file_name = 'DSC00109_2.JPG'
        fh = repository['2006'][file_name].open()
    else:
        try:
            fh = zeit.cms.interfaces.ICMSContent(file_name).open()
        except TypeError:
            fh = open(file_name, 'rb')
    extension = os.path.splitext(file_name)[-1].lower()

    group = zeit.content.image.imagegroup.ImageGroup()
    group.master_images = (('desktop', 'master-image' + extension),)
    repository['group'] = group
    image = zeit.content.image.image.LocalImage()
    with image.open('w') as out:
        out.write(fh.read())
    fh.close()
    repository['group'][group.master_image] = image
    return repository['group']


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZOPE_LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):

    layer = WSGI_LAYER


class StaticBrowserTestCase(zeit.cms.testing.BrowserTestCase):

    layer = HTTP_STATIC_LAYER


class SeleniumTestCase(zeit.cms.testing.SeleniumTestCase):

    layer = WEBDRIVER_LAYER
