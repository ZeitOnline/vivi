import urllib.parse
import urllib.request
import zeit.newsletter.interfaces
import zope.interface


@zope.interface.implementer(zeit.newsletter.interfaces.IRenderer)
class Renderer:

    def __init__(self, host):
        self.host = host
        if self.host.endswith('/'):
            self.host = self.host[:-1]

    def __call__(self, content):
        return dict(
            html=self.get_format(content, 'html'),
            text=self.get_format(content, 'txt'),
        )

    def get_format(self, content, format):
        url = self.url(content, format=format)
        try:
            return urllib.request.urlopen(
                url, timeout=60).read().decode('utf-8')
        except Exception as e:
            raise RuntimeError('Failed to load %r: %s' % (url, e))

    def url(self, content, **params):
        if not params:
            params = ''
        else:
            params = '?' + urllib.parse.urlencode(params)
        path = urllib.parse.urlparse(content.uniqueId).path
        return self.host + path + params


@zope.interface.implementer(zeit.newsletter.interfaces.IRenderer)
def renderer_from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.newsletter')
    return Renderer(config['renderer-host'])
