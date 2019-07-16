
import unittest
import doctest
import zeit.connector.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
        'profiling.txt',
        optionflags=zeit.connector.testing.optionflags))
    return suite
