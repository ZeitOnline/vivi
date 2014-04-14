import json
import requests
import zeit.push.interfaces
import zope.interface


class Connection(object):

    zope.interface.implements(zeit.push.interfaces.IPushNotifier)

    base_url = 'https://api.parse.com/1'

    def __init__(self, application_id, rest_api_key):
        self.application_id = application_id
        self.rest_api_key = rest_api_key

    def send(self, text, link, title=None):
        data = {
            'where': {},
            'data': {
                # Parse.com payload
                'alert': text,
                'title': title,  # Android only

                # App-specific payload
                'alert-title': title,
                'url': link,
            }
        }
        headers = {
            'X-Parse-Application-Id': self.application_id,
            'X-Parse-REST-API-Key': self.rest_api_key,
            'Content-Type': 'application/json',
        }
        response = requests.post(
            '%s/push' % self.base_url, data=json.dumps(data), headers=headers)

        if 200 <= response.status_code < 400:
            return
        if response.status_code < 500:
            error = response.json()
            message = error['error']
            if 'code' in error:
                message += ' (code=%s)' % error['code']
            raise zeit.push.interfaces.WebServiceError(message)
        raise zeit.push.interfaces.TechnicalError(response.text)


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
def from_product_config():
    # soft dependency
    import zope.app.appsetup.product
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.push')
    return Connection(
        config['parse-application-id'], config['parse-rest-api-key'])
