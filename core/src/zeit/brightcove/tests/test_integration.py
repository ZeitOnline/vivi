# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest


class CommonMetadataTest(unittest.TestCase):

    def get_metadata(self):
        from zeit.brightcove.integration import CommonMetadata
        video = mock.Mock()
        metadata = CommonMetadata(video)
        return video, metadata

    def test_getattr_should_get_data_from_context(self):
        video, metadata = self.get_metadata()
        self.assertTrue(metadata.serie, video.serie)

    def test_getattr_should_raise_for_non_commonmetata_keys(self):
        video, metadata = self.get_metadata()
        try:
            metadata.foo
        except AttributeError, e:
            self.assertEqual(('foo',), e.args)
        else:
            self.fail('AttributeError not raised')

    def test_should_provide_unique_id(self):
        video, metadata = self.get_metadata()
        video.uniqueId = mock.sentinel.unique_id
        self.assertEqual(mock.sentinel.unique_id, metadata.uniqueId)

    def test_setting_attributes_should_change_adapted_object(self):
        video, metadata = self.get_metadata()
        metadata.teaserTitle = mock.sentinel.teaserTitle
        self.assertEqual(mock.sentinel.teaserTitle, video.title)
        metadata.copyrights = mock.sentinel.copyrights
        self.assertEqual(mock.sentinel.copyrights, video.copyrights)
