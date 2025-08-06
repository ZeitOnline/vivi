import importlib.resources
import time
import urllib.parse

import requests

import zeit.cms.testing


HERE = importlib.resources.files(__package__)


class BQEmulatorLayer(zeit.cms.testing.Layer):
    defaultBases = (zeit.cms.testing.DOCKER_LAYER,)

    container_image = 'ghcr.io/goccy/bigquery-emulator:0.6.6'

    def setUp(self):
        port = zeit.cms.testing.get_random_port()
        project = 'vivi-test'
        dataset = 'export'
        self['bq_container'] = zeit.cms.testing.DOCKER_LAYER.run_container(
            self.container_image,
            command=(
                f'bigquery-emulator --project={project} '
                f'--data-from-yaml=/mnt/fixtures/bigquery.yaml'
            ),
            platform='linux/amd64',  # required on mac/arm, superfluous otherwise
            detach=True,
            remove=True,
            ports={9050: port},
            volumes={f'{HERE}/tests/fixtures': {'bind': '/mnt/fixtures', 'mode': 'ro'}},
        )
        self['dsn'] = f'bigquery://{project}:{port}/{dataset}'
        self['port'] = port
        self.wait_for_startup(self['dsn'])

    def wait_for_startup(self, dsn, timeout=10, sleep=0.2):
        url = urllib.parse.urlparse(dsn)
        http = requests.Session()

        slept = 0
        while slept < timeout:
            slept += sleep
            time.sleep(sleep)
            try:
                r = http.get(
                    f'http://localhost:{url.port}/bigquery/v2/projects/{url.hostname}/datasets{url.path}/tables'
                )
                r.raise_for_status()
            except Exception:
                pass
            else:
                http.close()
                return
        print(self['bq_container'].logs(timestamps=True).decode('utf-8'))
        raise RuntimeError('%s did not start up' % dsn)

    def tearDown(self):
        del self['dsn']
        self['bq_container'].stop()
        del self['bq_container']


BQ_SERVER_LAYER = BQEmulatorLayer()


class ConfigLayer(zeit.cms.testing.ProductConfigLayer):
    defaultBases = (BQ_SERVER_LAYER,)

    def __init__(self):
        super().__init__({})

    def setUp(self):
        # Set by BQ_SERVER_LAYER
        self.config['dsn'] = self['dsn']
        super().setUp()


BQ_CONFIG_LAYER = ConfigLayer()


BQ_ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    config_file='ftesting-bigquery.zcml',
    bases=(zeit.cms.testing.CONFIG_LAYER, BQ_CONFIG_LAYER),
)
BIGQUERY_LAYER = zeit.cms.testing.ZopeLayer(BQ_ZCML_LAYER)


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(zeit.cms.testing.CONFIG_LAYER)
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER)
