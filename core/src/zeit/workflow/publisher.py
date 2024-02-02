import requests
import zope.app.appsetup.product
import zope.interface

import zeit.cms.workflow.interfaces
import zeit.workflow.interfaces


class PublisherError(Exception):
    def __init__(self, url, status, errors):
        super().__init__()
        self.url = url
        self.status = status
        self.errors = errors


@zope.interface.implementer(zeit.cms.workflow.interfaces.IPublisher)
class Publisher:
    def request(self, items, method):
        if not items:
            return

        config = zope.app.appsetup.product.getProductConfiguration('zeit.workflow')
        publisher_base_url = config['publisher-base-url']
        if not publisher_base_url.endswith('/'):
            publisher_base_url += '/'

        headers = {}
        hostname = config.get('publisher-host')
        if hostname:
            headers['host'] = hostname

        url = f'{publisher_base_url}{method}'
        r = requests.post(url, json=items, headers=headers)
        if r.status_code != 200:
            raise PublisherError(r.url, r.status_code, r.json()['errors'])


@zope.interface.implementer(zeit.cms.workflow.interfaces.IPublisher)
class MockPublisher:
    def request(self, items, method):
        return
