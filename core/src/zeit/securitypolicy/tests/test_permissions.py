from zeit.securitypolicy.testing import make_xls_test
import os.path
import unittest
import xlrd


def test_suite():
    book = xlrd.open_workbook(os.path.join(os.path.dirname(__file__), '../test.xls'))
    sheet = book.sheet_by_index(0)

    suite = unittest.TestSuite()

    username_row = 1
    username_column_start = 3

    for expected_column in range(username_column_start, sheet.ncols):
        username = sheet.cell_value(username_row, expected_column)
        if not username:
            continue

        cases = []
        start_row = None
        for row in range(2, sheet.nrows):
            if start_row is None:
                start_row = row
            skin = sheet.cell_value(row, 0)
            path = sheet.cell_value(row, 1)
            form = sheet.cell_value(row, 2)
            expected = sheet.cell_value(row, expected_column)
            if path:
                cases.append((skin, path, form, expected))
            if cases and (not path or row == sheet.nrows - 1):
                description = 'test.xls rows %d-%d for %s' % (start_row + 1, row, username)
                suite.addTest(make_xls_test(username, cases, description))
                cases = []
                start_row = None

    # Picked up by gocept.pytestlayer (the layer on the XLSCase is ignored)
    suite.layer = list(suite)[0].layer
    return suite
