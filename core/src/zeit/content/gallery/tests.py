# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import PIL
import os
import unittest
import zeit.cms.testing
import zeit.workflow.tests
import zope.app.testing.functional


GalleryLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'GalleryLayer', allow_teardown=True)

GalleryWorkflowLayer = zeit.workflow.tests.WorkflowLayerFactory(
    os.path.join(os.path.dirname(__file__), 'ftesting-workflow.zcml'),
    __name__, 'GalleryWorkflowLayer', allow_teardown=True)


class TestGalleryStorer(zeit.cms.testing.FunctionalTestCase):

    layer = GalleryLayer

    def test_store(self):
        gallery = zeit.content.gallery.gallery.Gallery()
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        gallery.image_folder = repository['2007']
        zeit.content.gallery.testing.add_image('2007', '01.jpg')
        zeit.content.gallery.testing.add_image('2007', '02.jpg')
        gallery.reload_image_folder()

        entry = gallery['01.jpg']
        pil = PIL.Image.open(entry.image.open())
        zeit.imp.interfaces.IStorer(entry).store('10x10', pil)
        self.assertEqual(['01.jpg', '01.jpg-10x10.jpg', '02.jpg'],
                         list(gallery.keys()))
        self.assertEqual([True, False, False], [
            x.hidden for x in gallery.values()])



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'reference.txt',
        layer=GalleryLayer))
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'workflow.txt',
        product_config={'zeit.workflow': zeit.workflow.tests.product_config},
        layer=GalleryWorkflowLayer))
    suite.addTest(unittest.makeSuite(TestGalleryStorer))
    return suite
