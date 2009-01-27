# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import subprocess
import sys
import webbrowser
import xml.sax.saxutils
import zc.selenium.pytest
import zeit.cms.testing
import zope.component


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

    def __call__(self):
        zeit.cms.testing.setup_product_config()


class Test(zc.selenium.pytest.Test):

    def setUp(self):
        super(Test, self).setUp()
        self.open('/@@setup-product-config', auth=None)

    def tearDown(self):
        super(Test, self).tearDown()
        self.selenium.open('http://%s/@@reset-mock-connector' %
                           self.selenium.server)

    def click_label(self, label):
        self.selenium.click('//label[contains(string(.), %s)]' %
                            xml.sax.saxutils.quoteattr(label))

    def open(self, path, auth='user:userpw'):
        if auth:
            auth = auth + '@'
        else:
            auth = ''
        self.selenium.open(
            'http://%s%s/++skin++cms%s' % (auth, self.selenium.server, path))
