import zeit.cms.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'indicator.txt', package='zeit.cms.workflow.browser'
    )
