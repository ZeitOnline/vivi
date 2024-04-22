from unittest import mock
import logging
import unittest

import zeit.brightcove.testing


class VideoIdResolverTest(zeit.brightcove.testing.FunctionalTestCase):
    def test_video_id_should_be_resolved_to_unique_id(self):
        with mock.patch('zeit.connector.mock.Connector.search') as search:
            search.return_value = iter((('http://xml.zeit.de/video/2010-03/1234',),))
            self.assertEqual(
                'http://xml.zeit.de/video/2010-03/1234',
                zeit.brightcove.resolve.resolve_video_id('1234'),
            )

    def test_should_raise_if_no_object_is_found(self):
        with mock.patch('zeit.connector.mock.Connector.search') as search:
            search.return_value = iter(())
            self.assertRaises(LookupError, zeit.brightcove.resolve.resolve_video_id, '1234')

    def test_should_raise_and_warn_if_multiple_objects_are_found(self):
        log = logging.getLogger('zeit.brightcove.resolve')
        with mock.patch('zeit.connector.mock.Connector.search') as search:
            with mock.patch.object(log, 'warning') as log_warning:
                search.return_value = iter(
                    (
                        ('http://xml.zeit.de/video/2010-03/1234',),
                        ('http://xml.zeit.de/video/2010-03/1234',),
                    )
                )
                self.assertRaises(LookupError, zeit.brightcove.resolve.resolve_video_id, '1234')
                warning = log_warning.call_args
                self.assertFalse(warning is None)
                self.assertTrue('1234' in warning[0][0])


class QueryVideoIdTest(unittest.TestCase):
    def test_should_pass_video_to_resolver(self):
        from zeit.brightcove.resolve import query_video_id

        with mock.patch('zeit.brightcove.resolve.resolve_video_id') as rvi:
            query_video_id(mock.sentinel.avalue)
        rvi.assert_called_with(mock.sentinel.avalue)

    def test_should_return_value(self):
        from zeit.brightcove.resolve import query_video_id

        with mock.patch('zeit.brightcove.resolve.resolve_video_id') as rvi:
            rvi.return_value = mock.sentinel.result
            self.assertEqual(mock.sentinel.result, query_video_id(mock.sentinel.avalue))

    def test_should_return_None_on_lookup_error(self):
        from zeit.brightcove.resolve import query_video_id

        with mock.patch('zeit.brightcove.resolve.resolve_video_id') as rvi:
            rvi.side_effect = LookupError
            self.assertIsNone(query_video_id(mock.sentinel.avalue))

    def test_should_return_default_on_lookup_error(self):
        from zeit.brightcove.resolve import query_video_id

        with mock.patch('zeit.brightcove.resolve.resolve_video_id') as rvi:
            rvi.side_effect = LookupError
            self.assertEqual(
                mock.sentinel.default, query_video_id(mock.sentinel.avalue, mock.sentinel.default)
            )


class BackwardCompatibleUniqueIdsTest(zeit.brightcove.testing.FunctionalTestCase):
    def test_videos_should_be_resolvable(self):
        from zeit.cms.interfaces import ICMSContent

        expected_unique_id = 'http://xml.zeit.de/testcontent'
        with mock.patch('zeit.brightcove.resolve.resolve_video_id') as rvi:
            rvi.return_value = expected_unique_id
            result = ICMSContent('http://video.zeit.de/video/1234')
        self.assertEqual(expected_unique_id, result.uniqueId)
        rvi.assert_called_with('1234')
