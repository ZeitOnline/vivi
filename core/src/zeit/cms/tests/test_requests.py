from unittest import mock
import requests.adapters
import requests.exceptions
import time
import zeit.cms.testing


class SlowAdapter(requests.adapters.BaseAdapter):

    def send(self, request, **kwargs):
        time.sleep(float(request.headers.get('X-Sleep', '0')))
        return requests.Response()

    def close(self):
        pass


class SignalTimeoutTest(zeit.cms.testing.ZeitCmsTestCase):

    def setUp(self):
        super().setUp()
        self.session = requests.Session()
        self.session.mount('slow://', SlowAdapter())

    def test_signal_timeout_is_not_invoked_on_timeout_tuple(self):
        # If someone specifically set a connect and read timeout tuple,
        # we want to preserve requests' intended behaviour.
        # SlowAdapter ignores touple timeouts, so lets see if our signal
        # timeout patch leaves the slow request be slow.
        resp = self.session.get(
            'slow://example.com/',
            headers={'X-Sleep': '0.2'}, timeout=(0.01, 0.01))
        self.assertTrue(isinstance(resp, requests.Response))

    def test_signal_timeout_is_not_invoked_in_worker_thread(self):
        # Registering signal handlers can only be done within a main thread.
        # If it fails, we revert to requests original timeout mechanics.
        # This test also utilizes SlowAdapter ignoring the timeout kwarg.
        with mock.patch('signal.signal') as sig_func:
            sig_func.side_effect = ValueError()
            resp = self.session.get(
                'slow://example.com/',
                headers={'X-Sleep': '0.1'}, timeout=0.01)
            self.assertTrue(isinstance(resp, requests.Response))

    def test_signal_timeout_should_abort_slow_responses(self):
        # Finally, we want to see a timeout exception risen by our patched
        # signal request function.
        with self.assertRaises(requests.exceptions.Timeout):
            self.session.get(
                'slow://example.com/',
                headers={'X-Sleep': '0.1'}, timeout=0.01)
