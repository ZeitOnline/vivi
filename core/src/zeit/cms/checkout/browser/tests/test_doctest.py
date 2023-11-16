import zeit.cms.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt', 'conflict.txt', package='zeit.cms.checkout.browser'
    )
