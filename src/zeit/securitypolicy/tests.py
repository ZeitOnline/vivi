# Copyright (c) 2007-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import os.path
import unittest
import urllib
import xlrd
import zeit.brightcove.testing
import zeit.cms.testing
import zeit.connector.interfaces
import zeit.imp.tests
import zope.component
import zope.component.hooks
import zope.testbrowser.testing


SecurityPolicyLayer = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=(
        zeit.cms.testing.cms_product_config +
        zeit.imp.tests.product_config +
        zeit.brightcove.testing.product_config))


class TestSecurityPolicyXLSSheet(zeit.cms.testing.FunctionalTestCaseCommon):

    layer = SecurityPolicyLayer

    def __init__(self, username, cases, description):
        super(TestSecurityPolicyXLSSheet, self).__init__()
        self.username = username
        self.cases = cases
        self.description = description

        self.browser = zope.testbrowser.testing.Browser()
        self.browser.raiseHttpErrors = False
        if username != 'anonymous':
            password = self.username + 'pw'
            self.browser.addHeader(
                'Authorization', 'Basic %s:%s' % (self.username, password))

    def tearDown(self):
        self.connector._reset()
        super(TestSecurityPolicyXLSSheet, self).tearDown()

    def runTest(self):
        for skin, path, form, expected in self.cases:
            if skin.strip() == 'python:':
                test = self  # needed by the eval() call below
                site = zope.component.hooks.getSite()
                zope.component.hooks.setSite(self.getRootFolder())
                try:
                    # XXX pass variables in explicitly
                    eval(path)
                finally:
                    zope.component.hooks.setSite(site)
                continue
            path_with_skin = 'http://localhost/++skin++%s%s' % (skin, path)
            path_with_skin = path_with_skin % dict(username=self.username)

            if form:
                self.browser.post(
                    # XXX pass variables in explicitly
                    path_with_skin, urllib.urlencode(eval(form)))
            else:
                self.browser.open(path_with_skin)

            status, msg = self.browser.headers['Status'].split(' ', 1)
            self.assertEquals(
                (int(status) < 400), expected,
                '%s: %s (expected <400: %s)\n%s' % (
                    path.encode('utf8'), status, bool(expected),
                    self.browser.contents))

    def __str__(self):
        return '%s (%s.%s)' % (
            self.description,
            self.__class__.__module__, self.__class__.__name__)

    @property
    def connector(self):
        return zope.component.getUtility(zeit.connector.interfaces.IConnector)


def xls_tests():
    book = xlrd.open_workbook(os.path.join(
        os.path.dirname(__file__), 'test.xls'))
    sheet = book.sheet_by_index(0)

    suite = unittest.TestSuite()

    username_row = 1
    username_column_start = 3

    for expected_column in xrange(username_column_start, sheet.ncols):
        username = sheet.cell_value(username_row, expected_column)
        if not username:
            continue

        cases = []
        start_row = None
        for row in xrange(2, sheet.nrows):
            if start_row is None:
                start_row = row
            skin = sheet.cell_value(row, 0)
            path = sheet.cell_value(row, 1)
            form = sheet.cell_value(row, 2)
            expected = sheet.cell_value(row, expected_column)
            if path:
                cases.append((skin, path, form, expected))
            if cases and (not path or row == sheet.nrows-1):
                description = 'test.xls rows %d-%d for %s' % (
                    start_row+1, row, username)
                suite.addTest(TestSecurityPolicyXLSSheet(
                    username, cases, description))
                cases = []
                start_row = None

    return suite


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(xls_tests())
    return suite
