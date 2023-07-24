import requests

import zope.app.appsetup.product
import zope.interface

import zeit.workflow.interfaces
import zeit.cms.workflow.interfaces


class PublisherError(Exception):

    def __init__(self, url, status, errors):
        super().__init__()
        self.url = url
        self.status = status
        self.errors = errors


@zope.interface.implementer(zeit.cms.workflow.interfaces.IPublisher)
class Publisher:

    def request(self, to_process_list, method):
        if not to_process_list:
            return

        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        publisher_base_url = config['publisher-base-url']
        if not publisher_base_url.endswith('/'):
            publisher_base_url += '/'

        headers = {}
        hostname = config.get('publisher-host')
        if hostname:
            headers['host'] = hostname

        url = f'{publisher_base_url}{method}'
        json = [zeit.workflow.interfaces.IPublisherData(obj)(method)
                for obj in to_process_list]
        r = requests.post(url=url, json=json, headers=headers)
        if r.status_code != 200:
            raise PublisherError(r.url, r.status_code, r.json()['errors'])


@zope.interface.implementer(zeit.cms.workflow.interfaces.IPublisher)
class MockPublisher:

    def request(self, to_process_list, method):
        return
