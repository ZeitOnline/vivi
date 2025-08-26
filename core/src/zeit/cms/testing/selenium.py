import logging
import os
import sys
import xml.sax

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import gocept.selenium
import gocept.selenium.wd_selenese
import pytest
import selenium.webdriver
import transaction
import zope.component
import zope.error.interfaces

from .layer import Layer
from .zope import FunctionalTestCase


@pytest.mark.selenium()
class SeleniumTestCase(gocept.selenium.WebdriverSeleneseTestCase, FunctionalTestCase):
    skin = 'cms'
    log_errors = False
    log_errors_ignore = ()
    level = 2

    TIMEOUT = int(os.environ.get('ZEIT_SELENIUM_TIMEOUT', 10))

    window_width = 1100
    window_height = 600

    def setUp(self):
        super().setUp()
        self.layer['selenium'].setTimeout(self.TIMEOUT * 1000)

        if self.log_errors:
            error_log = zope.component.getUtility(zope.error.interfaces.IErrorReportingUtility)
            error_log.copy_to_zlog = True
            error_log._ignored_exceptions = self.log_errors_ignore
            self.log_handler = logging.StreamHandler(sys.stdout)
            logging.root.addHandler(self.log_handler)
            self.old_log_level = logging.root.level
            logging.root.setLevel(logging.WARN)
            transaction.commit()

        self.original_windows = set(self.selenium.getAllWindowIds())
        self.original_width = self.selenium.getEval('window.outerWidth')
        self.original_height = self.selenium.getEval('window.outerHeight')
        self.selenium.setWindowSize(self.window_width, self.window_height)
        self.execute('window.localStorage.clear()')

    def tearDown(self):
        super().tearDown()
        if self.log_errors:
            logging.root.removeHandler(self.log_handler)
            logging.root.setLevel(self.old_log_level)

        current_windows = set(self.selenium.getAllWindowIds())
        for window in current_windows - self.original_windows:
            self.selenium.selectWindow(window)
            self.selenium.close()
        self.selenium.selectWindow()

        self.selenium.setWindowSize(self.original_width, self.original_height)
        # open a neutral page to stop all pending AJAX requests
        self.open('/@@test-setup-auth')

    def open(self, path, auth='user:userpw'):
        if auth:
            auth += '@'
        self.selenium.open(
            'http://%s%s/++skin++%s%s' % (auth, self.selenium.server, self.skin, path)
        )

    def click_label(self, label):
        self.selenium.click('//label[contains(string(.), %s)]' % xml.sax.saxutils.quoteattr(label))

    js_globals = """\
        var document = window.document;
        var zeit = window.zeit;
    """

    def execute(self, text):
        return self.selenium.selenium.execute_script(self.js_globals + text)

    def eval(self, text):
        return self.execute('return ' + text)

    def wait_for_condition(self, text):
        self.selenium.waitForCondition(
            self.js_globals
            + """\
        return Boolean(%s);
        """
            % text
        )

    def wait_for_dotted_name(self, dotted_name):
        partial = []
        for part in dotted_name.split('.'):
            partial.append(part)
            self.wait_for_condition('.'.join(partial))

    def add_by_autocomplete(self, text, widget):
        s = self.selenium
        s.type(widget, text)
        autocomplete_item = 'css=.ui-menu-item a'
        s.waitForElementPresent(autocomplete_item)
        s.waitForVisible(autocomplete_item)
        s.click(autocomplete_item)
        s.waitForNotVisible('css=.ui-menu')


class WebdriverLayer(Layer, gocept.selenium.WebdriverLayer):
    def get_firefox_webdriver_args(self):
        options = selenium.webdriver.FirefoxOptions()

        if self['headless']:
            options.add_argument('-headless')

        if profile_path := os.environ.get('GOCEPT_WEBDRIVER_FF_PROFILE'):
            options.set_preference('profile', profile_path)

        # Save downloads always to disk into a predefined dir.
        options.set_preference('browser.download.folderList', 2)
        options.set_preference('browser.download.manager.showWhenStarting', False)
        options.set_preference('browser.download.dir', str(self['selenium_download_dir']))
        options.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/pdf')
        options.set_preference('pdfjs.disabled', True)

        # The default 'info' is still way too verbose
        options.log.level = 'error'
        options.binary_location = os.environ.get('GOCEPT_WEBDRIVER_FF_BINARY', '')
        return {'options': options}

    def setUp(self):
        super().setUp()
        self['selenium'] = gocept.selenium.wd_selenese.Selenese(
            self['seleniumrc'], self['http_address'], SeleniumTestCase.TIMEOUT * 1000
        )

        # NOTE: Massively kludgy workaround. It seems that Firefox has a timing
        # issue with HTTP auth and AJAX calls: if you open a page that requires
        # auth and has AJAX calls to further pages that require the same auth,
        # sometimes those AJAX calls come back as 401 (nothing to do with
        # Selenium, we've seen this against the actual server).
        #
        # It seems that opening a page and then giving it a little time
        # to settle in is enough to work around this issue.
        s = self['selenium']
        # XXX It seems something is not ready immediately?!??
        s.pause(1000)
        # XXX Credentials are duplicated from SeleniumTestCase.open().
        s.open('http://user:userpw@%s/++skin++vivi/@@test-setup-auth' % self['http_address'])
        # We don't really know how much time the browser needs until it's
        # satisfied, or how we could determine this.
        s.pause(1000)

    def _stop_selenium(self):
        super()._stop_selenium()
        if 'seleniumrc' not in self:
            return
        self['seleniumrc'].command_executor._conn.clear()
        binary = getattr(self['seleniumrc'], 'binary', None)
        if binary is not None:
            binary._log_file.close()


def assertOrdered(self, locator1, locator2):
    if self._find(locator2).id not in {
        x.id for x in self.selenium.find_elements(By.XPATH, locator1 + '/following-sibling::*')
    }:
        raise self.failureException(
            'Element order did not match expected %r,%r' % (locator1, locator2)
        )


gocept.selenium.wd_selenese.Selenese.assertOrdered = assertOrdered


def clickAt(self, locator, coordString):
    x, y = coordString.split(',')
    x = int(x)
    y = int(y)
    elem = self._find(locator)
    # selenium-4 switched the reference point for move_to_element to center,
    # but selenium-3 hat top/left, so we have to calculate the inverse here.
    x -= int(elem.rect['width'] / 2)
    y -= int(elem.rect['height'] / 2)
    ActionChains(self.selenium).move_to_element_with_offset(elem, x, y).click().perform()


gocept.selenium.wd_selenese.Selenese.clickAt = clickAt
