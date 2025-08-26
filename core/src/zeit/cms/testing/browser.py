from urllib.parse import urljoin
import base64
import json

import gocept.testing.assertion
import lxml.cssselect
import lxml.etree
import lxml.html
import transaction
import webtest.lint
import zope.testbrowser.browser

from .zope import FunctionalTestCase


class Browser(zope.testbrowser.browser.Browser):
    follow_redirects = True
    xml_strict = False

    def __init__(self, wsgi_app):
        super().__init__(wsgi_app=wsgi_app)

    def open(self, url, *args, **kw):
        if url.startswith('/'):
            url = 'http://localhost/++skin++vivi' + url
        return super().open(url, *args, **kw)

    def login(self, username, password):
        auth = base64.b64encode(('%s:%s' % (username, password)).encode('utf-8')).decode('ascii')
        self.addHeader('Authorization', 'Basic %s' % auth)

    def reload(self):
        # Don't know what the superclass is doing here, exactly, but it's not
        # helpful at all, so we reimplement it in a hopefully more sane way.
        if self._response is None:
            raise zope.testbrowser.browser.BrowserStateError('No URL has yet been .open()ed')
        self.open(self.url)

    def _processRequest(self, url, make_request):
        self._document = None
        transaction.commit()
        old_site = zope.component.hooks.getSite()
        zope.component.hooks.setSite(None)
        old_interaction = zope.security.management.queryInteraction()
        zope.security.management.endInteraction()
        try:
            # No super call, since we had to copy&paste the whole method.
            self._do_processRequest(url, make_request)
        finally:
            zope.component.hooks.setSite(old_site)
            if old_interaction:
                zope.security.management.thread_local.interaction = old_interaction

    # copy&paste from superclass _processRequest to plug in `follow_redirects`
    def _do_processRequest(self, url, make_request):
        with self._preparedRequest(url) as reqargs:
            self._history.add(self._response)
            resp = make_request(reqargs)
            if self.follow_redirects:
                remaining_redirects = 100  # infinite loops protection
                while remaining_redirects and resp.status_int in zope.testbrowser.browser.REDIRECTS:
                    remaining_redirects -= 1
                    url = urljoin(url, resp.headers['location'])
                    with self._preparedRequest(url) as reqargs:
                        resp = self.testapp.get(url, **reqargs)
                assert remaining_redirects > 0, 'redirect chain looks infinite'
            self._setResponse(resp)
            self._checkStatus()

    HTML_PARSER = lxml.html.HTMLParser(encoding='UTF-8')
    _document = None

    @property
    def document(self):
        """Return an lxml.html.HtmlElement instance of the response body."""
        if self._document is not None:
            return self._document
        if self.contents is None:
            return None
        if self.xml_strict:
            self._document = lxml.etree.fromstring(self.contents)
        else:
            self._document = lxml.html.document_fromstring(self.contents, parser=self.HTML_PARSER)
        return self._document

    def xpath(self, selector, **kw):
        """Return a list of lxml.HTMLElement instances that match a given
        XPath selector.
        """
        if self.document is None:
            return None
        return self.document.xpath(selector, **kw)

    def cssselect(self, selector, **kw):
        return self.xpath(lxml.cssselect.CSSSelector(selector).path, **kw)


# Allow webtest to handle file download result iterators
webtest.lint.isinstance = zope.security.proxy.isinstance


class BrowserAssertions(gocept.testing.assertion.Ellipsis):
    # XXX backwards-compat method signature for existing tests, should probably
    # be removed at some point
    def assert_ellipsis(self, want, got=None):
        if got is None:
            got = self.browser.contents
        self.assertEllipsis(want, got)

    def assert_json(self, want, got=None):
        if got is None:
            got = self.browser.contents
        data = json.loads(got)
        self.assertEqual(want, data)
        return data


class BrowserTestCase(FunctionalTestCase, BrowserAssertions):
    login_as = ('user', 'userpw')

    def setUp(self):
        super().setUp()
        self.browser = Browser(self.layer['wsgi_app'])
        if isinstance(self.login_as, str):  # BBB:
            self.login_as = self.login_as.split(':')
        self.browser.login(*self.login_as)
