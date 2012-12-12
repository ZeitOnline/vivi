# Copyright (c) 2007-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from __future__ import with_statement
import gocept.selenium.ztk
import pkg_resources
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.content.image.image
import zeit.content.image.imagegroup
import zope.component


ImageLayer = zeit.cms.testing.ZCMLLayer(
    pkg_resources.resource_filename(__name__, 'ftesting.zcml'),
    __name__, 'ImageLayer', allow_teardown=True)

selenium_layer = gocept.selenium.ztk.Layer(ImageLayer)


def create_image_group(file_name=None):
    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    group = zeit.content.image.imagegroup.ImageGroup()
    repository['image-group'] = group
    group = repository['image-group']
    for filename in ('new-hampshire-450x200.jpg',
                     'new-hampshire-artikel.jpg',
                     'obama-clinton-120x120.jpg'):
        image = zeit.content.image.image.LocalImage()
        image.mimeType = 'image/jpeg'
        fh = image.open('w')
        if file_name is None:
            file_name = pkg_resources.resource_filename(
                __name__, 'browser/testdata/%s' % filename)
        fh.write(open(file_name, 'rb').read())
        fh.close()
        group[filename] = image
    return group


def create_image_group_with_master_image(file_name=None):
    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    group = zeit.content.image.imagegroup.ImageGroup()
    group.master_image = u'master-image.jpg'
    repository['group'] = group
    image = zeit.content.image.image.LocalImage()
    image.mimeType = 'image/jpeg'
    if file_name is None:
        fh = repository['2006']['DSC00109_2.JPG'].open()
    else:
        fh = open(file_name)
    image.open('w').write(fh.read())
    repository['group']['master-image.jpg'] = image
    return repository['group']
