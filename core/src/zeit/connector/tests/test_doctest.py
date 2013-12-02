# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import doctest
import unittest
import zeit.connector.connector
import zeit.connector.testing


def test_suite():
    suite = unittest.TestSuite()

    real = zeit.connector.testing.FunctionalDocFileSuite(
        'connector.txt',
        'locking.txt',
        'resource.txt',
        'search-ft.txt',
        'uuid.txt',
    )
    real.level = 2
    suite.addTest(real)

    mock = zeit.connector.testing.FunctionalDocFileSuite(
        'mock.txt',
        'uuid.txt',
        layer=zeit.connector.testing.mock_connector_layer,
    )
    suite.addTest(mock)

    long_running = zeit.connector.testing.FunctionalDocFileSuite(
        'longrunning.txt',
        'stressing.txt',
    )
    long_running.level = 3
    suite.addTest(long_running)

    functional = zeit.connector.testing.FunctionalDocFileSuite(
        'cache.txt',
        'functional.txt',
        'invalidator.txt',
        'invalidation-events.txt',
        layer=zeit.connector.testing.zope_connector_layer,
    )
    suite.addTest(functional)

    suite.addTest(doctest.DocTestSuite(zeit.connector.connector))
    suite.addTest(doctest.DocFileSuite(
        'search.txt',
        optionflags=doctest.ELLIPSIS,
        package='zeit.connector'))

    return suite
