from __future__ import with_statement
import gocept.httpserverlayer.wsgi
import gocept.selenium
import mimetypes
import os.path
import pkg_resources
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.content.image.image
import zeit.content.image.imagegroup
import zope.component


product_config = """
<product-config zeit.content.image>
    variant-source file://{fixtures}/tests/fixtures/variants.xml
</product-config>
""".format(fixtures=pkg_resources.resource_filename(__name__, '.'))


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=product_config + zeit.cms.testing.cms_product_config)
WSGI_LAYER = zeit.cms.testing.WSGILayer(
    name='WSGILayer', bases=(ZCML_LAYER,))
HTTP_LAYER = gocept.httpserverlayer.wsgi.Layer(
    name='HTTPLayer', bases=(WSGI_LAYER,))
WD_LAYER = gocept.selenium.WebdriverLayer(
    name='WebdriverLayer', bases=(HTTP_LAYER,))
WEBDRIVER_LAYER = gocept.selenium.WebdriverSeleneseLayer(
    name='WebdriverSeleneseLayer', bases=(WD_LAYER,))


def create_local_image(filename):
    image = zeit.content.image.image.LocalImage(mimeType='image/jpeg')
    fh = image.open('w')
    file_name = pkg_resources.resource_filename(
        __name__, 'browser/testdata/%s' % filename)
    fh.write(open(file_name, 'rb').read())
    fh.close()
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
        fh = open(file_name)
    extension = os.path.splitext(file_name)[-1].lower()

    group = zeit.content.image.imagegroup.ImageGroup()
    group.master_image = u'master-image' + extension
    repository['group'] = group
    image = zeit.content.image.image.LocalImage()
    image.mimeType = mimetypes.types_map[extension]
    image.open('w').write(fh.read())
    repository['group'][group.master_image] = image
    return repository['group']
