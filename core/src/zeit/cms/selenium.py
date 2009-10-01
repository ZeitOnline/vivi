# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import cjson
import subprocess
import sys
import transaction
import urllib
import webbrowser
import xml.sax.saxutils
import zc.selenium.pytest
import zeit.cms.testing
import zope.component
import zope.error.error


if sys.platform == 'darwin':
    # Register a Firefox browser for Mac OS X.
    class MacOSXFirefox(webbrowser.BaseBrowser):

        def open(self, url, new=0, autoraise=1):
            proc = subprocess.Popen(
                ['/usr/bin/open', '-a', 'Firefox', url])
            proc.communicate()
    webbrowser.register('Firefox', MacOSXFirefox, None, -1)


class ResetMockConnector(object):

    def __call__(self):
        zope.component.getUtility(
            zeit.connector.interfaces.IConnector)._reset()
        return "Done."


class SetupProductConfig(object):

    def __call__(self, product_config):
        zeit.cms.testing.setup_product_config(cjson.decode(product_config))


class Test(zc.selenium.pytest.Test):

    product_config = {}
    skin = 'cms'

    def setUp(self):
        super(Test, self).setUp()
        zope.component.getUtility(
            zope.error.interfaces.IErrorReportingUtility).copy_to_zlog = True
        transaction.commit()
        self.set_product_config(self.product_config)

    def tearDown(self):
        super(Test, self).tearDown()
        self.selenium.open('http://%s/@@reset-mock-connector' %
                           self.selenium.server)

    def set_product_config(self, product_config):
        product_config = cjson.encode(product_config)
        query = urllib.urlencode(dict(product_config=product_config))
        self.open('/@@setup-product-config?' + query, auth=None)

    def click_label(self, label):
        self.selenium.click('//label[contains(string(.), %s)]' %
                            xml.sax.saxutils.quoteattr(label))

    def open(self, path, auth='user:userpw'):
        if auth:
            auth = auth + '@'
        else:
            auth = ''
        self.selenium.open(
            'http://%s%s/++skin++%s%s' % (
                auth, self.selenium.server, self.skin, path))
