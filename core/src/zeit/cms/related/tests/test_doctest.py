import zeit.cms.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'related.txt',
        package='zeit.cms.related',
    )
