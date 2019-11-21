import six.moves.urllib.parse
import six.moves.urllib.request
import zeit.newsletter.interfaces
import zope.interface


class Renderer(object):

    zope.interface.implements(zeit.newsletter.interfaces.IRenderer)

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
            return six.moves.urllib.request.urlopen(
                url, timeout=60).read().decode('utf-8')
        except Exception as e:
            raise RuntimeError('Failed to load %r: %s' % (url, e))

    def url(self, content, **params):
        if not params:
            params = ''
        else:
            params = '?' + six.moves.urllib.parse.urlencode(params)
        path = six.moves.urllib.parse.urlparse(content.uniqueId).path
        return self.host + path + params


@zope.interface.implementer(zeit.newsletter.interfaces.IRenderer)
def renderer_from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.newsletter')
    return Renderer(config['renderer-host'])
