import zeit.connector.testing


def test_suite():
    return zeit.connector.testing.FunctionalDocFileSuite(
        'cache.txt',
        'search.txt',
        'uuid.txt',
        layer=zeit.connector.testing.MOCK_CONNECTOR_LAYER,
    )
