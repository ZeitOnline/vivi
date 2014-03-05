# Copyright (c) 2013 gocept gmbh & co. kg
# See also LICENSE.txt

import ZODB.utils
import os.path
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

    def mktemp(self, dir=None):
        self.assertEqual(None, self.tempfile)
        self.tempfile = self.orig_mktemp(dir)
        return self.tempfile

    def test_temporary_file_for_thumbnail_is_cleaned_up_after_request(self):
        b = self.browser
        b.open('http://localhost/++skin++cms/repository/'
               '2006/DSC00109_2.JPG/@@preview')
        self.assertFalse(os.path.exists(self.tempfile))
