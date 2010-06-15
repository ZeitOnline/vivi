# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.connector.testing


def test_suite():
    suite = unittest.TestSuite()

    real = zeit.connector.testing.FunctionalDocFileSuite(
        'connector.txt',
        'locking.txt',
        'resource.txt',
        'search.txt',
        'uuid.txt',
        )
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

    return suite
