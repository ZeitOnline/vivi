from zeit.cms.interfaces import CONFIG_CACHE
import base64
import json
import pkg_resources
import requests
import requests.exceptions
import requests.utils
import zeit.content.author.interfaces
import zope.interface
import zope.security.management


@zope.interface.implementer(zeit.content.author.interfaces.IHonorar)
class Honorar(object):

    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password

    def search(self, query, count=10):
        result = self._request('POST /layouts/RESTautorenStamm/_find', json={
            'query': [
                {'nameGesamt': query},
                {'typ': '4', 'omit': 'true'},
                {'status': '>=50', 'omit': 'true'},
            ],
            'sort': [{'fieldName': 'nameGesamt', 'sortOrder': 'ascend'}],
            'limit': str(count),
        })
        return [x['fieldData'] for x in result['response']['data']]

    def create(self, data):
        interaction = zope.security.management.getInteraction()
        principal = interaction.participations[0].principal
        data['anlageAccount'] = 'vivi.%s' % principal.id
        # 1=nat. Person, 2=jur. Person, 3=Pseudonym, 4=anonym/Buchhaltung
        data['typ'] = '1'
        result = self._request('GET /layouts/leer/records/1', params={
            'script': 'restNeuAutor',
            'script.param': b64encode(json.dumps(data))
        })
        return result['response']['scriptResult']

    def _request(self, request, retries=0, **kw):
        if retries > 1:
            raise ValueError('Request %s failed' % request)

        verb, path = request.split(' ')
        method = getattr(requests, verb.lower())
        try:
            r = method(self.url + path, headers={
                'Authorization': 'Bearer %s' % self.auth_token(),
                'User-Agent': requests.utils.default_user_agent(
                    'zeit.content.author-%s/python-requests' % (
                        pkg_resources.get_distribution('vivi.core').version))
            }, **kw)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.HTTPError as err:
            status = getattr(err.response, 'status_code', 599)
            if status == 401:
                self.auth_token.invalidate(self)
                return self._request(request, retries=retries + 1)
            if status == 500:
                r = err.response.json()
                messages = r.get('messages', ())
                if not messages:
                    raise
                if messages[0].get('code') == '401':
                    # "No records match the request", wonderful API. :-(
                    return {'response': {'data': []}}
                elif messages[0].get('code') == '101':
                    # Even wonderfuller API: `create` with GET has no "normal"
                    # FileMaker result, so it complains.
                    return r
                else:
                    err.args += tuple(messages)
            raise

    @CONFIG_CACHE.cache_on_arguments()
    def auth_token(self):
        r = requests.post(self.url + '/sessions',
                          auth=(self.username, self.password),
                          headers={'Content-Type': 'application/json'})
        r.raise_for_status()
        return r.headers.get('X-FM-Data-Access-Token')


def b64encode(text):
    return base64.b64encode(text.encode('ascii')).decode('ascii')


@zope.interface.implementer(zeit.content.author.interfaces.IHonorar)
def from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.content.author')
    return Honorar(
        config['honorar-url'],
        config['honorar-username'],
        config['honorar-password'])
