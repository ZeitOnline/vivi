# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import SimpleHTTPServer
import __future__
import os
import pkg_resources
import re
import zeit.cms.testing
import zope.testing.doctest
import zope.testing.renormalizing


product_config = """
<product-config zeit.content.cp>
    block-layout-source file://%s
    cp-extra-url file://%s
    cp-feed-max-items 200
    cp-types-url file://%s
    feed-update-minimum-age 30
    rss-folder rss
    rules-url file://%s
</product-config>

<product-config zeit.workflow>
    publish-script cat
    path-prefix
</product-config>
""" % (pkg_resources.resource_filename(__name__, 'layout.xml'),
    pkg_resources.resource_filename(__name__, 'cpextra.xml'),
    pkg_resources.resource_filename(__name__, 'cp-types.xml'),
    pkg_resources.resource_filename('zeit.content.cp.tests.fixtures',
                                    'example_rules.py'))


layer = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=zeit.cms.testing.cms_product_config + product_config)



class RequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    serve_from = pkg_resources.resource_filename(__name__, 'tests/feeds/')
    serve_favicon = False

    def send_head(self):
        if self.path == '/favicon.ico' and not self.serve_favicon:
            self.path = '/does-not-exist'
        return SimpleHTTPServer.SimpleHTTPRequestHandler.send_head(self)

    def translate_path(self, path):
        cur_path = os.getcwd()
        os.chdir(self.serve_from)
        try:
            return SimpleHTTPServer.SimpleHTTPRequestHandler.translate_path(
                self, path)
        finally:
            os.chdir(cur_path)

    def guess_type(self, path):
        return 'application/xml'

    def log_message(self, format, *args):
        pass


HTTPLayer, httpd_port = zeit.cms.testing.HTTPServerLayer(RequestHandler)


class FeedServer(HTTPLayer, layer):

    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass



checker = zope.testing.renormalizing.RENormalizing([
    (re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'),
     "<GUID>"),
    (re.compile('[0-9a-f]{32}'), "<MD5>"),
    (re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}[T ][0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?(\+[0-9]{2}:[0-9]{2})?'),
     "<ISO DATE>"),
    (re.compile('[A-Z][a-z]{2}, [0-9]{2} [A-Z][a-z]{2} [0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2} [+-][0-9]{4}'),
     "<RFC822 DATE>"),
])

checker.transformers[0:0] = zeit.cms.testing.checker.transformers


def FunctionalDocFileSuite(*args, **kw):
    kw.setdefault('checker', checker)
    kw.setdefault('layer', layer)
    kw.setdefault('globs', dict(with_statement=__future__.with_statement))
    kw['package'] = zope.testing.doctest._normalize_module(kw.get('package'))
    return zeit.cms.testing.FunctionalDocFileSuite(*args, **kw)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = layer
