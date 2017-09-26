import requests
import zeit.push.interfaces
import zope.interface


class Connection(object):
    """Writes an event to InfluxDB which can be shown in Grafana."""

    zope.interface.implements(zeit.push.interfaces.IPushNotifier)

    def __init__(self, base_url, database, user, password, series):
        self.base_url = base_url
        self.database = database
        self.user = user
        self.password = password
        self.series = series

    def send(self, text, link, **kw):
        template = kw.get('payload_template', '').replace('.json', '')
        data = [{
            'name': self.series,
            'columns': ['title', 'tags', 'text'],
            'points': [[template, 'push', link]],
        }]
        try:
            requests.post(
                '{url}/db/{database}/series'.format(
                    url=self.base_url, database=self.database),
                params={'u': self.user, 'p': self.password}, json=data)
        except:
            pass


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
def from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.push')
    return Connection(config['influxdb-url'], config['influxdb-db'],
                      config['influxdb-user'], config['influxdb-password'],
                      config['influxdb-series'])
