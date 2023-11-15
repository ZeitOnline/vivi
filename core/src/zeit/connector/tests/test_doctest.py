import pytest
import unittest
import zeit.cms.testing
import zeit.connector.connector
import zeit.connector.testing


def test_suite():
    suite = unittest.TestSuite()

    mock = zeit.connector.testing.FunctionalDocFileSuite(
        'uuid.txt',
        layer=zeit.connector.testing.MOCK_CONNECTOR_LAYER,
    )
    suite.addTest(mock)

    functional = zeit.connector.testing.FunctionalDocFileSuite(
        'cache.txt',
        'functional.txt',
        'invalidator.txt',
        'invalidation-events.txt',
        layer=zeit.connector.testing.ZOPE_CONNECTOR_LAYER,
    )
    zeit.connector.testing.mark_doctest_suite(functional, pytest.mark.slow)
    suite.addTest(functional)

    suite.addTest(zeit.cms.testing.DocFileSuite('search.txt', package='zeit.connector'))

    return suite
