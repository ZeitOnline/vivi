# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component as grok
import urllib
import urllib2
import urlparse
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
            html=self.get_format(content, 'newsletter_html'),
            text=self.get_format(content, 'newsletter_text'),
        )

    def get_format(self, content, format):
        return urllib2.urlopen(
            self.url(content, format=format), timeout=60).read()

    def url(self, content, **params):
        if not params:
            params = ''
        else:
            params = '?' + urllib.urlencode(params)
        path = urlparse.urlparse(content.uniqueId).path
        return self.host + path + params


def renderer_from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.newsletter')
    return Renderer(config['renderer-host'])

grok.global_utility(
    renderer_from_product_config, zeit.newsletter.interfaces.IRenderer)
