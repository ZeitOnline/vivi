
import unittest
import doctest
import zeit.cms.testing


def test_suite():
    suite = doctest.DocFileSuite(
        'profiling.txt',
        package='zeit.connector',
        optionflags=zeit.cms.testing.optionflags)
    # These are meant for manual profiling
    suite = unittest.skip(suite)
    return suite
