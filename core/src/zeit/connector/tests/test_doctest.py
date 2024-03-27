import zeit.connector.testing


def test_suite():
    return zeit.connector.testing.FunctionalDocFileSuite(
        'cache.txt',
        'functional.txt',
        'invalidation-events.txt',
        'search.txt',
        layer=zeit.connector.testing.ZOPE_DAV_CONNECTOR_LAYER,
    )
