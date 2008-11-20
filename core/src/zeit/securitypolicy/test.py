# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt

import os.path
import unittest
import xlrd
import zope.app.testing.functional
import zope.component

import zeit.cms.testing
import zeit.connector.interfaces


SecurityPolicyLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'SecurityPolicyLayer', allow_teardown=True)


class TestSecurityPolicyXLSSheet(
    zope.app.testing.functional.BrowserTestCase):

    layer = SecurityPolicyLayer

    def __init__(self, username, cases, description):
        super(TestSecurityPolicyXLSSheet, self).__init__()
        self.username = username
        self.cases = cases
        self.description = description

        if username == 'anonymous':
            self.basic = None
        else:
            password = self.username + 'pw'
            self.basic = '%s:%s' % (self.username, password)

    def setUp(self):
        super(TestSecurityPolicyXLSSheet, self).setUp()
        zeit.cms.testing.setup_product_config()

    def tearDown(self):
        self.connector._reset()
        super(TestSecurityPolicyXLSSheet, self).tearDown()

    def runTest(self):
        # if form XXX
        for skin, path, form, expected in self.cases:
            path_with_skin = '/++skin++%s%s' % (skin, path)
            path_with_skin = path_with_skin % dict(username=self.username)
            response = self.publish(
                path_with_skin, basic=self.basic, handle_errors=True)
            status = response.getStatus()
            self.assertEquals(
                (status < 400), expected,
                '%s: %s (expected <400: %s)' % (path, status, bool(expected)))

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
