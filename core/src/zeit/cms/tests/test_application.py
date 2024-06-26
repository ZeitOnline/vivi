import importlib.metadata
import urllib.error

from prometheus_client.parser import text_string_to_metric_families as prometheus
import packaging.requirements

import zeit.cms.testing


def test_pip_check_for_all_extras():
    """We use a [default] extra to simplify extracting the [test] extra
    into a separate requirements file, but extras are not covered by `pip check`
    """
    # Adapted from pypa/pip#4824
    requirements = [
        packaging.requirements.Requirement(x)
        for x in importlib.metadata.metadata('vivi.core').get_all('Requires-Dist')
    ]
    for req in requirements:
        installed = importlib.metadata.distribution(req.name)
        assert req.specifier.contains(installed.version, prereleases=True)


class Prometheus(zeit.cms.testing.ZeitCmsBrowserTestCase):
    def test_prometheus_metrics_are_exposed(self):
        b = self.browser

        def check():
            b.open('http://localhost/metrics')
            assert b.headers.get('status') == '200 OK'
            metrics = [x.name for x in prometheus(b.contents)]
            assert 'http_server_duration_milliseconds' in metrics

        for _ in range(2):  # Hopefully cover bootstrapping cases
            with self.assertRaises(urllib.error.HTTPError) as info:
                b.open('http://localhost/nonexistent')
                assert info.exception.status == 404

            check()

        # Ensure that the metric does not disappear when there are no measurements
        check()
