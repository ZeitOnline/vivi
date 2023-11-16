import zeit.cms.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt', 'cache.txt', 'preference.txt', 'file.txt', package='zeit.cms.repository'
    )
