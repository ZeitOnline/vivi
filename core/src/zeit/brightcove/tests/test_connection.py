from unittest import mock
import os
import pytest
import requests.exceptions
import unittest
import zeit.brightcove.connection


@pytest.mark.slow()
class APIIntegration(unittest.TestCase):

    level = 2

    def test_invalid_accesstoken_refreshes_and_retries_request(self):
        api = zeit.brightcove.connection.CMSAPI(
            'https://cms.api.brightcove.com/v1/accounts/18140073001',
            'https://oauth.brightcove.com/v4',
            os.environ.get('ZEIT_BRIGHTCOVE_CLIENT_ID'),
            os.environ.get('ZEIT_BRIGHTCOVE_CLIENT_SECRET'),
            timeout=2)
        try:
            data = api._request('GET /video_fields')
            self.assertIn('custom_fields', data.keys())
        except requests.exceptions.Timeout:
            pass

    def test_playback_api_authenticates_with_policy_key(self):
        api = zeit.brightcove.connection.PlaybackAPI(
            'https://edge.api.brightcove.com/playback/v1/accounts/18140073001',
            os.environ.get('ZEIT_BRIGHTCOVE_POLICY_KEY'),
            timeout=2)
        try:
            data = api._request('GET /videos/5622601784001')
            assert 'zeitmagazin' in data['tags']
        except requests.exceptions.Timeout:
            pass


class CMSAPI(unittest.TestCase):

    def test_auth_failed_retries_request(self):
        api = zeit.brightcove.connection.CMSAPI('', '', '', '', None)
        with mock.patch.object(api, '_retrieve_access_token') as token:
            with mock.patch('requests.request') as request:
                token.return_value = 'token'
                request_calls = []

                def fail_once(*args, **kw):
                    if not request_calls:
                        request_calls.append(1)
                        err = requests.exceptions.RequestException()
                        err.response = mock.Mock()
                        err.response.status_code = 401
                        raise err
                    response = mock.MagicMock()
                    response.__iter__.return_value = ()
                    response.json.return_value = {}
                    return response
                request.side_effect = fail_once
                api._request('GET /foo', {'body': True}, {'params': 2})
                self.assertEqual(2, request.call_count)
                request.assert_called_with(
                    'get', '/foo', headers={'Authorization': 'Bearer token'},
                    json={'body': True}, params={'params': 2}, timeout=None)

    def test_aborts_after_max_retries(self):
        api = zeit.brightcove.connection.CMSAPI('', '', '', '', None)
        with mock.patch.object(api, '_retrieve_access_token') as token:
            with mock.patch('requests.request') as request:
                token.return_value = ''
                request.side_effect = requests.exceptions.RequestException()
                request.side_effect.response = mock.Mock()
                request.side_effect.response.status_code = 401

                with self.assertRaises(RuntimeError):
                    api._request('GET /video_fields')
                self.assertEqual(2, token.call_count)

    def test_paginates_through_playlists(self):
        api = zeit.brightcove.connection.CMSAPI('', '', '', '', None)
        with mock.patch.object(api, '_request') as request:
            request.side_effect = [
                {'count': 5},
                [{'id': 1}, {'id': 2}],
                [{'id': 2}, {'id': 3}, {'id': 4}],
                [],
            ]
            result = api.get_all_playlists()
            self.assertEqual(
                [{'id': 1}, {'id': 2}, {'id': 3}, {'id': 4}], list(result))
            self.assertEqual(
                0, request.call_args_list[1][1]['params']['offset'])
            self.assertEqual(
                2, request.call_args_list[2][1]['params']['offset'])
            self.assertEqual(
                5, request.call_args_list[3][1]['params']['offset'])


class PlayerAPI(unittest.TestCase):

    def test_converts_sources(self):
        api = zeit.brightcove.connection.PlaybackAPI('', '', None)
        with mock.patch.object(api, '_request') as request:
            request.return_value = {'sources': [{
                'asset_id': '83006421001',
                'codec': 'H264',
                'container': 'MP4',
                'duration': 85163,
                'encoding_rate': 1264000,
                'height': 720,
                'remote': False,
                'size': 13453446,
                'src': 'https://brightcove.hs.llnwd.net/e1/pd/...',
                'uploaded_at': '2010-05-05T08:26:48.704Z',
                'width': 1280,
            }]}
            data = api.get_video('myid')
        self.assertEqual(1, len(data['renditions']))
        src = data['renditions'][0]
        self.assertEqual(1280, src.frame_width)
        self.assertEqual('https://brightcove.hs.llnwd.net/e1/pd/...', src.url)
        self.assertEqual(85163, src.video_duration)
