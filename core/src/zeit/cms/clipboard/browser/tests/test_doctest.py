import zeit.cms.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt', 'clip.txt', package='zeit.cms.clipboard.browser'
    )
