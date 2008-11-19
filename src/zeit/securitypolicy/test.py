# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt

import os.path
import unittest
import xlrd
import zope.app.testing.functional

import zeit.cms.testing


SecurityPolicyLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'SecurityPolicyLayer', allow_teardown=True)


class TestSecurityPolicyXLSSheet(
    zope.app.testing.functional.BrowserTestCase):

    layer = SecurityPolicyLayer

    def __init__(self, username, skin, path, form, expected):
        zope.app.testing.functional.BrowserTestCase.__init__(self)
        self.username = username
        self.skin = skin
        self.path = path
        self.form = form
        self.expected = expected

        if username == 'anonymous':
            self.basic = None
        else:
            password = self.username + 'pw'
            self.basic = '%s:%s' % (self.username, password)

    def setUp(self):
        zeit.cms.testing.setup_product_config()

    def runTest(self):
        # if form XXX
        path_with_skin = '/++skin++%s%s' % (self.skin, self.path)
        response = self.publish(
            path_with_skin, basic=self.basic, handle_errors=True)
        status = response.getStatus()
        self.assertEquals(
            (status < 400), self.expected,
            '%s (expected <400: %s)' % (status, bool(self.expected)))

    def __str__(self):
        return '%s: [%s]%s (%s.%s)' % (
            self.username, self.skin, self.path,
            self.__class__.__module__, self.__class__.__name__)


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

        for row in xrange(2, sheet.nrows):
            skin = sheet.cell_value(row, 0)
            path = sheet.cell_value(row, 1)
            form = sheet.cell_value(row, 2)
            expected = sheet.cell_value(row, expected_column)
            if not path:
                continue

            suite.addTest(TestSecurityPolicyXLSSheet(
                username, skin, path, form, expected))

    return suite


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(xls_tests())
    return suite
