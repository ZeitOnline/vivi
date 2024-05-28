import logging

import requests
import zope.interface

import zeit.newsimport.interfaces


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.newsimport.interfaces.IDPA)
class DPA:
    def __init__(self, url):
        self.api_url = url

    def _request(self, verb, url, raise_for_status=True):
        with requests.Session() as http:
            method = getattr(http, verb.lower())
            response = method('{}{}'.format(self.api_url, url))
            if raise_for_status:
                response.raise_for_status()
            return response

    def get_entries(self):
        result = self._request('GET', '/entries.json')
        return result.json()['entries']

    def delete_entry(self, receipt):
        response = self._request(
            'DELETE', '/entry/{receipt}'.format(receipt=receipt), raise_for_status=False
        )
        return response


def set_up_weblines_profile():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.newsimport')
    return DPA(config['weblines-url'])


def set_up_nextline_profile():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.newsimport')
    return DPA(config['nextline-url'])
