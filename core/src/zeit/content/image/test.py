# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt

import os.path
import unittest
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.content.image.image
import zeit.content.image.imagegroup
import zope.app.testing.functional
import zope.component
from zope.testing import doctest


ImageLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'ImageLayer', allow_teardown=True)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'syndication.txt',
        'transform.txt',
        'masterimage.txt',
        layer=ImageLayer))
    return suite


def create_image_group():
    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    group = zeit.content.image.imagegroup.ImageGroup()
    repository['image-group'] = group
    group = repository['image-group']
    for filename in ('new-hampshire-450x200.jpg',
                     'new-hampshire-artikel.jpg',
                     'obama-clinton-120x120.jpg'):
        image = zeit.content.image.image.LocalImage()
        image.contentType = 'image/jpeg'
        fh = image.open('w')
        fh.write(open(os.path.join(
            os.path.dirname(__file__),
            'browser', 'testdata', filename), 'rb').read())
        fh.close()
        group[filename] = image
    return group


def create_image_group_with_master_image():
    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    repository['group'] = zeit.content.image.imagegroup.ImageGroup()
    image = zeit.content.image.image.LocalImage()
    image.open('w').write(
        repository['2006']['DSC00109_2.JPG'].open().read())
    zope.interface.alsoProvides(image,
                                zeit.content.image.interfaces.IMasterImage)
    repository['group']['master-image.jpg'] = image
    return repository['group']
