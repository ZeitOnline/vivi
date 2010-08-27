# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest


class CommonMetadataTest(unittest.TestCase):

    def test_getattr_should_get_data_from_context(self):
        from zeit.brightcove.integration import CommonMetadata
        video = mock.Mock()
        metadata = CommonMetadata(video)
        self.assertTrue(metadata.serie, video.serie)

    def test_getattr_should_raise_for_non_commonmetata_keys(self):
        from zeit.brightcove.integration import CommonMetadata
        video = mock.Mock()
        metadata = CommonMetadata(video)
        try:
            metadata.foo
        except AttributeError, e:
            self.assertEqual(('foo',), e.args)
        else:
            self.fail('AttributeError not raised')
