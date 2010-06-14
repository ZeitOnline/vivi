# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.testing import doctest
import unittest
import zeit.connector.testing
import zope.app.testing.functional


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
        'connector.txt',
        'locking.txt',
        'mock.txt',
        'resource.txt',
        'search.txt',
        'uuid.txt',
        optionflags=zeit.connector.testing.optionflags,
        package='zeit.connector'))

    long_running = doctest.DocFileSuite(
        'longrunning.txt',
        'stressing.txt',
        optionflags=zeit.connector.testing.optionflags,
        package='zeit.connector')
    long_running.level = 3
    suite.addTest(long_running)

    functional = zope.app.testing.functional.FunctionalDocFileSuite(
        'cache.txt',
        'functional.txt',
        'invalidator.txt',
        'invalidation-events.txt',
        optionflags=zeit.connector.testing.optionflags,
        package='zeit.connector')
    functional.layer = zeit.connector.testing.real_connector_layer
    suite.addTest(functional)

    return suite
