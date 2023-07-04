from json import dumps

import requests

import zope.app.appsetup.product
import zope.interface

import zeit.workflow.interfaces
import zeit.cms.workflow.interfaces


class PublishError(Exception):
    pass


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
        response = requests.post(
            url=url, json=json, headers=headers)
        if response.status_code != 200:
            publisher_parts = dumps(response.json()['errors'])
            raise PublishError(
                f'Calling publisher on {url} failed '
                f'with {response.status_code}: {response.reason}. '
                f'Details: {publisher_parts}')


@zope.interface.implementer(zeit.cms.workflow.interfaces.IPublisher)
class MockPublisher:

    def request(self, to_process_list, method):
        return