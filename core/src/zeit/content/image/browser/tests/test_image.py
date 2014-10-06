# Copyright (c) 2013 gocept gmbh & co. kg
# See also LICENSE.txt

import ZODB.utils
import os.path
import unittest
import zeit.cms.testing
import zeit.content.image.testing


class BlobCleanupTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.image.testing.ZCML_LAYER

    def setUp(self):
        super(BlobCleanupTest, self).setUp()
        self.orig_mktemp = ZODB.utils.mktemp
        ZODB.utils.mktemp = self.mktemp
        self.tempfile = None

    def tearDown(self):
        ZODB.utils.mktemp = self.orig_mktemp
        super(BlobCleanupTest, self).tearDown()

    def mktemp(self, dir=None, prefix='tmp'):
        self.assertEqual(None, self.tempfile)
        self.tempfile = self.orig_mktemp(dir, prefix)
        return self.tempfile

    def test_temporary_file_for_thumbnail_is_cleaned_up_after_request(self):
        b = self.browser
        b.open('http://localhost/++skin++cms/repository/'
               '2006/DSC00109_2.JPG/@@preview')
        self.assertFalse(os.path.exists(self.tempfile))


class ImageEdit(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.image.testing.ZCML_LAYER

    def setUp(self):
        super(ImageEdit, self).setUp()
        b = self.browser
        b.open(
            'http://localhost/++skin++vivi/repository'
            '/2006/DSC00109_2.JPG/@@checkout')
        b.getControl(
            name='form.copyrights.0..combination_00').value = 'required'

    @unittest.skip(
        'Disabled because the frontend does not interpret rewritten links '
        'correctly yet.')
    def test_rewrites_links_from_www_zeit_de_to_xml_zeit_de(self):
        b = self.browser
        b.getControl('Links to').value = 'http://www.zeit.de/foo/bar'
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)
        self.assertEqual(
            'http://xml.zeit.de/foo/bar', b.getControl('Links to').value)

    def test_leaves_other_links_alone(self):
        b = self.browser
        b.getControl('Links to').value = 'http://example.de/foo/bar'
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)
        self.assertEqual(
            'http://example.de/foo/bar', b.getControl('Links to').value)
