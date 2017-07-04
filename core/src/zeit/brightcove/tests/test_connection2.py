import mock
import os
import pytest
import requests.exceptions
import unittest
import zeit.brightcove.connection2


@pytest.mark.slow
class APIIntegration(unittest.TestCase):

    level = 2

    def setUp(self):
        self.api = zeit.brightcove.connection2.CMSAPI(
            'https://cms.api.brightcove.com/v1/accounts/18140073001',
            'https://oauth.brightcove.com/v4',
            os.environ.get('ZEIT_BRIGHTCOVE_CLIENT_ID'),
            os.environ.get('ZEIT_BRIGHTCOVE_CLIENT_SECRET'),
            timeout=2)

    def test_invalid_accesstoken_refreshes_and_retries_request(self):
        data = self.api._request('GET /video_fields')
        self.assertIn('custom_fields', data.keys())


class CMSAPI(unittest.TestCase):

    def test_aborts_after_max_retries(self):
        api = zeit.brightcove.connection2.CMSAPI('', '', '', '', None)
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
        api = zeit.brightcove.connection2.CMSAPI('', '', '', '', None)
        with mock.patch.object(api, '_request') as request:
            request.side_effect = [
                {'count': 5},
                [{'id': 1}, {'id': 2}],
                [{'id': 2}, {'id': 3}, {'id': 4}],
                [],
            ]
            result = api.get_all_playlists()
            self.assertEqual(
                [{'id': 1}, {'id': 2}, {'id': 3}, {'id': 4}], result)
            self.assertEqual(
                0, request.call_args_list[1][1]['params']['offset'])
            self.assertEqual(
                2, request.call_args_list[2][1]['params']['offset'])
            self.assertEqual(
                5, request.call_args_list[3][1]['params']['offset'])
