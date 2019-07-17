
import unittest
import doctest
import zeit.cms.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
        'profiling.txt',
        optionflags=zeit.cms.testing.optionflags))
    return suite
